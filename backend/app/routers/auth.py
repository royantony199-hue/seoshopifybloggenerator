#!/usr/bin/env python3
"""
Authentication router for user management and API key handling
"""

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta
from typing import Optional

from app.core.database import get_db, User, Tenant
from app.core.config import settings

router = APIRouter()

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# Pydantic models
class UserCreate(BaseModel):
    email: str
    password: str
    first_name: str
    last_name: str
    company_name: str
    openai_api_key: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    role: str
    tenant_id: int
    tenant_name: str
    is_active: bool

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class ShopifyStoreSetup(BaseModel):
    store_name: str
    shop_url: str
    access_token: str
    blog_handle: str = "news"
    default_product_url: Optional[str] = None

# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash password"""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def authenticate_user(db: Session, email: str, password: str):
    """Authenticate user credentials"""
    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: int = payload.get("user_id")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    
    return user

# Routes
@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user and create tenant"""
    
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create tenant
    tenant_slug = user_data.company_name.lower().replace(" ", "-").replace(".", "")
    tenant = Tenant(
        name=user_data.company_name,
        slug=tenant_slug,
        subscription_plan="starter",
        subscription_status="trial",
        trial_ends_at=datetime.utcnow() + timedelta(days=14)
    )
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Create user
    hashed_password = get_password_hash(user_data.password)
    user = User(
        tenant_id=tenant.id,
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        role="admin",  # First user is admin
        openai_api_key=user_data.openai_api_key
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"user_id": user.id, "tenant_id": tenant.id})
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        tenant_id=tenant.id,
        tenant_name=tenant.name,
        is_active=user.is_active
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user"""
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Get tenant info
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create access token
    access_token = create_access_token(data={"user_id": user.id, "tenant_id": user.tenant_id})
    
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
        tenant_id=user.tenant_id,
        tenant_name=tenant.name if tenant else "",
        is_active=user.is_active
    )
    
    return Token(access_token=access_token, token_type="bearer", user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user information"""
    
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        first_name=current_user.first_name,
        last_name=current_user.last_name,
        role=current_user.role,
        tenant_id=current_user.tenant_id,
        tenant_name=tenant.name if tenant else "",
        is_active=current_user.is_active
    )

@router.put("/api-key")
async def update_openai_key(
    openai_api_key: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user's OpenAI API key"""
    
    # Validate API key by making a test call
    import openai
    try:
        client = openai.OpenAI(api_key=openai_api_key)
        # Test the API key with a minimal request
        response = client.models.list()
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid OpenAI API key"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid OpenAI API key: {str(e)}"
        )
    
    # Update user's API key
    current_user.openai_api_key = openai_api_key
    db.commit()
    
    return {"message": "OpenAI API key updated successfully"}

@router.post("/setup-complete")
async def complete_setup(
    store_data: ShopifyStoreSetup,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Complete initial setup by adding Shopify store"""
    
    # Validate Shopify credentials
    import requests
    try:
        headers = {
            'X-Shopify-Access-Token': store_data.access_token,
            'Content-Type': 'application/json'
        }
        response = requests.get(
            f"https://{store_data.shop_url}.myshopify.com/admin/api/2024-01/shop.json",
            headers=headers,
            timeout=10
        )
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid Shopify credentials"
            )
    except requests.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to validate Shopify store: {str(e)}"
        )
    
    # Create Shopify store record
    from app.core.database import ShopifyStore
    store = ShopifyStore(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        store_name=store_data.store_name,
        shop_url=store_data.shop_url,
        access_token=store_data.access_token,
        blog_handle=store_data.blog_handle,
        default_product_url=store_data.default_product_url,
        is_active=True
    )
    
    db.add(store)
    db.commit()
    db.refresh(store)
    
    return {
        "message": "Setup completed successfully",
        "store_id": store.id,
        "next_step": "upload_keywords"
    }