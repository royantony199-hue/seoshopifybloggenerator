#!/usr/bin/env python3
"""
Shopify OAuth 2.0 integration router

Handles OAuth flow for connecting Shopify stores via the Dev Dashboard app method.
This is required for stores that don't have the legacy "Develop apps" feature.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import secrets
import hashlib
import hmac
import requests
import logging

from app.core.database import get_db, ShopifyStore
from app.core.config import settings
from app.routers.demo_auth import get_demo_current_user
import os

# Fallback to direct env var read if pydantic-settings doesn't pick it up
def get_shopify_client_id():
    return get_shopify_client_id() or os.environ.get("SHOPIFY_CLIENT_ID")

def get_shopify_client_secret():
    return get_shopify_client_secret() or os.environ.get("SHOPIFY_CLIENT_SECRET")

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory state storage (use Redis in production)
oauth_states = {}


class OAuthInitRequest(BaseModel):
    """Request to start OAuth flow"""
    shop_url: str  # e.g., "bluelotusimaginal" (without .myshopify.com)
    store_name: str  # Display name for the store


class OAuthConnectResponse(BaseModel):
    """Response with OAuth authorization URL"""
    authorization_url: str
    state: str


class ConnectedStore(BaseModel):
    """Connected store info"""
    id: int
    store_name: str
    shop_url: str
    blog_handle: str
    custom_domain: Optional[str]
    is_active: bool
    connected_at: datetime


def verify_shopify_hmac(query_params: dict, secret: str) -> bool:
    """Verify Shopify's HMAC signature on callback"""
    hmac_value = query_params.pop('hmac', None)
    if not hmac_value:
        return False

    # Sort and encode parameters
    sorted_params = '&'.join([f"{k}={v}" for k, v in sorted(query_params.items())])
    computed_hmac = hmac.new(
        secret.encode('utf-8'),
        sorted_params.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(computed_hmac, hmac_value)


@router.post("/authorize", response_model=OAuthConnectResponse)
async def start_oauth_flow(
    request_obj: Request,
    request: OAuthInitRequest,
    db: Session = Depends(get_db)
):
    """
    Start Shopify OAuth flow.

    Returns an authorization URL that the frontend should redirect the user to.
    """
    client_id = get_shopify_client_id()
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Shopify OAuth not configured. Set SHOPIFY_CLIENT_ID in environment."
        )

    # Get current user
    current_user = await get_demo_current_user(db)

    # Generate secure state token
    state = secrets.token_urlsafe(32)

    # Determine redirect URI dynamically (production vs local)
    # Check if running on Railway or other production environment
    host = request_obj.headers.get("host", "localhost:8000")
    scheme = request_obj.headers.get("x-forwarded-proto", "http")

    if "railway.app" in host or "production" in host or scheme == "https":
        redirect_uri = f"https://{host}/api/shopify/oauth/callback"
    else:
        redirect_uri = settings.SHOPIFY_OAUTH_REDIRECT_URI

    # Store state with metadata (expires in 10 minutes)
    oauth_states[state] = {
        "shop_url": request.shop_url,
        "store_name": request.store_name,
        "user_id": current_user.id,
        "tenant_id": current_user.tenant_id,
        "redirect_uri": redirect_uri,
        "created_at": datetime.utcnow().isoformat()
    }

    # Build authorization URL
    shop_domain = f"{request.shop_url}.myshopify.com"
    auth_url = (
        f"https://{shop_domain}/admin/oauth/authorize"
        f"?client_id={get_shopify_client_id()}"
        f"&scope={settings.SHOPIFY_SCOPES}"
        f"&redirect_uri={redirect_uri}"
        f"&state={state}"
    )

    logger.info(f"Starting OAuth flow for shop: {request.shop_url}, redirect_uri: {redirect_uri}")

    return OAuthConnectResponse(
        authorization_url=auth_url,
        state=state
    )


@router.get("/callback")
async def oauth_callback(
    request: Request,
    code: str = Query(...),
    state: str = Query(...),
    shop: str = Query(...),
    hmac: str = Query(None),
    db: Session = Depends(get_db)
):
    """
    Handle Shopify OAuth callback.

    Exchanges the authorization code for an access token and stores it.
    """
    # Verify state to prevent CSRF
    if state not in oauth_states:
        logger.error(f"Invalid OAuth state: {state}")
        return HTMLResponse(
            content="""
            <html>
            <head><title>Connection Failed</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #e74c3c;">Connection Failed</h1>
                <p>Invalid or expired OAuth state. Please try connecting again.</p>
                <a href="/" style="color: #3498db;">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=400
        )

    state_data = oauth_states.pop(state)

    # Exchange code for access token
    token_url = f"https://{shop}/admin/oauth/access_token"

    try:
        # Use the redirect_uri that was stored when initiating the flow
        exchange_redirect_uri = state_data.get("redirect_uri", settings.SHOPIFY_OAUTH_REDIRECT_URI)

        response = requests.post(token_url, json={
            "client_id": get_shopify_client_id(),
            "client_secret": get_shopify_client_secret(),
            "code": code
        }, timeout=30)

        logger.info(f"Token exchange response status: {response.status_code}")

        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.text}")
            return HTMLResponse(
                content=f"""
                <html>
                <head><title>Connection Failed</title></head>
                <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                    <h1 style="color: #e74c3c;">Connection Failed</h1>
                    <p>Failed to get access token from Shopify.</p>
                    <p>Error: {response.text}</p>
                    <a href="/" style="color: #3498db;">Return to Dashboard</a>
                </body>
                </html>
                """,
                status_code=400
            )

        token_data = response.json()
        access_token = token_data.get("access_token")
        scope = token_data.get("scope", "")

        if not access_token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No access token in response"
            )

        # Extract shop URL (remove .myshopify.com)
        shop_url = shop.replace(".myshopify.com", "")

        # Check if store already exists
        existing_store = db.query(ShopifyStore).filter(
            ShopifyStore.tenant_id == state_data["tenant_id"],
            ShopifyStore.shop_url == shop_url
        ).first()

        if existing_store:
            # Update existing store's token
            existing_store.access_token = access_token
            existing_store.last_sync = datetime.utcnow()
            db.commit()
            store_id = existing_store.id
            logger.info(f"Updated existing store: {shop_url}")
        else:
            # Create new store
            new_store = ShopifyStore(
                tenant_id=state_data["tenant_id"],
                user_id=state_data["user_id"],
                store_name=state_data["store_name"],
                shop_url=shop_url,
                access_token=access_token,
                blog_handle="news",  # Default, can be changed later
                is_active=True
            )
            db.add(new_store)
            db.commit()
            db.refresh(new_store)
            store_id = new_store.id
            logger.info(f"Created new store: {shop_url}")

        # Return success page that closes the popup/redirects
        return HTMLResponse(
            content=f"""
            <html>
            <head>
                <title>Store Connected!</title>
                <script>
                    // If opened in popup, close it and refresh parent
                    if (window.opener) {{
                        window.opener.location.reload();
                        window.close();
                    }} else {{
                        // Otherwise redirect to dashboard
                        window.location.href = '/?store_connected={store_id}';
                    }}
                </script>
            </head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #27ae60;">Store Connected Successfully!</h1>
                <p>Your Shopify store <strong>{state_data['store_name']}</strong> has been connected.</p>
                <p>Scopes granted: {scope}</p>
                <p>Redirecting to dashboard...</p>
                <a href="/" style="color: #3498db;">Click here if not redirected</a>
            </body>
            </html>
            """
        )

    except requests.RequestException as e:
        logger.error(f"OAuth callback error: {str(e)}")
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>Connection Failed</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
                <h1 style="color: #e74c3c;">Connection Failed</h1>
                <p>Network error while connecting to Shopify.</p>
                <p>Error: {str(e)}</p>
                <a href="/" style="color: #3498db;">Return to Dashboard</a>
            </body>
            </html>
            """,
            status_code=500
        )


@router.get("/connected", response_model=list[ConnectedStore])
async def get_connected_stores(db: Session = Depends(get_db)):
    """Get all OAuth-connected stores for current user"""
    current_user = await get_demo_current_user(db)

    stores = db.query(ShopifyStore).filter(
        ShopifyStore.tenant_id == current_user.tenant_id,
        ShopifyStore.is_active == True
    ).all()

    return [
        ConnectedStore(
            id=store.id,
            store_name=store.store_name,
            shop_url=store.shop_url,
            blog_handle=store.blog_handle,
            custom_domain=store.custom_domain,
            is_active=store.is_active,
            connected_at=store.created_at
        )
        for store in stores
    ]


@router.post("/disconnect/{store_id}")
async def disconnect_store(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Disconnect a Shopify store (removes access token, keeps record)"""
    current_user = await get_demo_current_user(db)

    store = db.query(ShopifyStore).filter(
        ShopifyStore.id == store_id,
        ShopifyStore.tenant_id == current_user.tenant_id
    ).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    # Deactivate and clear token
    store.is_active = False
    store.access_token = ""
    db.commit()

    logger.info(f"Disconnected store: {store.shop_url}")

    return {"message": f"Store '{store.store_name}' disconnected successfully"}


@router.get("/test-connection/{store_id}")
async def test_store_connection(
    store_id: int,
    db: Session = Depends(get_db)
):
    """Test if a store's access token is still valid"""
    current_user = await get_demo_current_user(db)

    store = db.query(ShopifyStore).filter(
        ShopifyStore.id == store_id,
        ShopifyStore.tenant_id == current_user.tenant_id
    ).first()

    if not store:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Store not found"
        )

    if not store.access_token or store.access_token.startswith("demo_"):
        return {
            "connected": False,
            "demo_mode": True,
            "message": "Store is in demo mode (no real token)"
        }

    # Test the token by fetching shop info
    try:
        response = requests.get(
            f"https://{store.shop_url}.myshopify.com/admin/api/2024-10/shop.json",
            headers={
                "X-Shopify-Access-Token": store.access_token,
                "Content-Type": "application/json"
            },
            timeout=10
        )

        if response.status_code == 200:
            shop_data = response.json().get("shop", {})
            return {
                "connected": True,
                "shop_name": shop_data.get("name"),
                "shop_domain": shop_data.get("domain"),
                "plan": shop_data.get("plan_name"),
                "message": "Connection successful"
            }
        else:
            return {
                "connected": False,
                "error": response.text,
                "message": "Token may be invalid or revoked"
            }

    except requests.RequestException as e:
        return {
            "connected": False,
            "error": str(e),
            "message": "Network error testing connection"
        }
