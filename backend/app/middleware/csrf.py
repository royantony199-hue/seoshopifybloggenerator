#!/usr/bin/env python3
"""
CSRF Protection Middleware
"""

import secrets
import hmac
import hashlib
from fastapi import Request, HTTPException, status
from fastapi.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import logging

logger = logging.getLogger(__name__)

class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF Protection Middleware
    
    Protects against Cross-Site Request Forgery attacks by validating
    CSRF tokens on state-changing operations.
    """
    
    def __init__(self, app: ASGIApp, secret_key: str):
        super().__init__(app)
        self.secret_key = secret_key.encode('utf-8')
        self.csrf_exempt_paths = {
            '/docs',
            '/openapi.json',
            '/health',
            '/',
            '/api/auth/login',
            '/api/auth/register'
        }
        self.state_changing_methods = {'POST', 'PUT', 'DELETE', 'PATCH'}
    
    def generate_csrf_token(self, session_id: str = None) -> str:
        """Generate a CSRF token for the given session"""
        if not session_id:
            session_id = secrets.token_hex(16)
        
        # Create HMAC with session_id and random data
        random_data = secrets.token_bytes(32)
        message = session_id.encode('utf-8') + random_data
        signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
        
        # Combine session_id, random_data (hex), and signature
        token = f"{session_id}.{random_data.hex()}.{signature}"
        return token
    
    def validate_csrf_token(self, token: str, session_id: str = None) -> bool:
        """Validate a CSRF token"""
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return False
            
            token_session_id, random_hex, signature = parts
            
            # If session_id is provided, it must match the token
            if session_id and token_session_id != session_id:
                return False
            
            # Reconstruct the message and verify signature
            random_data = bytes.fromhex(random_hex)
            message = token_session_id.encode('utf-8') + random_data
            expected_signature = hmac.new(self.secret_key, message, hashlib.sha256).hexdigest()
            
            return hmac.compare_digest(signature, expected_signature)
        except (ValueError, TypeError) as e:
            logger.warning(f"CSRF token validation error: {e}")
            return False
    
    async def dispatch(self, request: Request, call_next):
        """Process the request with CSRF protection"""
        
        # Skip CSRF check for exempt paths
        if request.url.path in self.csrf_exempt_paths:
            response = await call_next(request)
            return response
        
        # Skip CSRF check for safe methods
        if request.method not in self.state_changing_methods:
            response = await call_next(request)
            # Add CSRF token to GET responses for forms
            if request.method == 'GET' and 'text/html' in request.headers.get('accept', ''):
                csrf_token = self.generate_csrf_token()
                response.headers['X-CSRF-Token'] = csrf_token
            return response
        
        # Validate CSRF token for state-changing methods
        csrf_token = None
        
        # Check for CSRF token in headers (preferred)
        csrf_token = request.headers.get('X-CSRF-Token')
        
        # Fallback: check in form data
        if not csrf_token and request.headers.get('content-type', '').startswith('application/x-www-form-urlencoded'):
            try:
                form_data = await request.form()
                csrf_token = form_data.get('csrf_token')
            except:
                pass
        
        # Validate token
        if not csrf_token:
            logger.warning(f"CSRF token missing for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="CSRF token missing"
            )
        
        if not self.validate_csrf_token(csrf_token):
            logger.warning(f"Invalid CSRF token for {request.method} {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid CSRF token"
            )
        
        # Process the request
        response = await call_next(request)
        return response


def get_csrf_token(secret_key: str) -> str:
    """Helper function to generate a CSRF token"""
    middleware = CSRFMiddleware(None, secret_key)
    return middleware.generate_csrf_token()