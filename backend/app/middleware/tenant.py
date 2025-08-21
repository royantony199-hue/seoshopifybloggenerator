#!/usr/bin/env python3
"""
Tenant isolation middleware
"""

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware for tenant isolation and context"""
    
    async def dispatch(self, request: Request, call_next):
        # Add tenant context if needed
        # This could be used for database connection routing
        # or additional tenant-specific logic
        
        response = await call_next(request)
        return response