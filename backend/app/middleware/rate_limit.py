#!/usr/bin/env python3
"""
Enhanced Rate limiting middleware with multiple strategies
"""

from fastapi import Request, Response, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
import time
import asyncio
import logging
from collections import defaultdict
from typing import Dict, List
from app.core.config import settings

logger = logging.getLogger(__name__)

class RateLimitMiddleware(BaseHTTPMiddleware):
    """Enhanced rate limiting middleware with per-endpoint and per-user limits"""
    
    def __init__(self, app):
        super().__init__(app)
        self.ip_requests: Dict[str, List[float]] = defaultdict(list)
        self.user_requests: Dict[str, List[float]] = defaultdict(list)
        self.endpoint_requests: Dict[str, List[float]] = defaultdict(list)
        self.cleanup_task = None
        self.start_cleanup_task()
    
    def start_cleanup_task(self):
        """Start background task to clean up old requests"""
        if self.cleanup_task is None:
            self.cleanup_task = asyncio.create_task(self.cleanup_old_requests())
    
    async def cleanup_old_requests(self):
        """Background task to periodically clean up old request records"""
        while True:
            try:
                await asyncio.sleep(300)  # Clean up every 5 minutes
                current_time = time.time()
                
                # Clean IP requests
                for ip in list(self.ip_requests.keys()):
                    self.ip_requests[ip] = [
                        req_time for req_time in self.ip_requests[ip]
                        if current_time - req_time < settings.RATE_LIMIT_WINDOW
                    ]
                    if not self.ip_requests[ip]:
                        del self.ip_requests[ip]
                
                # Clean user requests
                for user in list(self.user_requests.keys()):
                    self.user_requests[user] = [
                        req_time for req_time in self.user_requests[user]
                        if current_time - req_time < settings.RATE_LIMIT_WINDOW
                    ]
                    if not self.user_requests[user]:
                        del self.user_requests[user]
                
                # Clean endpoint requests
                for endpoint in list(self.endpoint_requests.keys()):
                    self.endpoint_requests[endpoint] = [
                        req_time for req_time in self.endpoint_requests[endpoint]
                        if current_time - req_time < settings.RATE_LIMIT_WINDOW
                    ]
                    if not self.endpoint_requests[endpoint]:
                        del self.endpoint_requests[endpoint]
                        
            except Exception as e:
                logger.error(f"Error in rate limit cleanup task: {e}")
    
    def get_client_identifier(self, request: Request) -> str:
        """Get client identifier, considering proxies"""
        # Check for forwarded IP headers (in order of preference)
        forwarded_for = request.headers.get('X-Forwarded-For')
        if forwarded_for:
            # Take the first IP in the chain
            return forwarded_for.split(',')[0].strip()
        
        real_ip = request.headers.get('X-Real-IP')
        if real_ip:
            return real_ip.strip()
        
        # Fallback to direct connection IP
        return request.client.host if request.client else "unknown"
    
    def get_user_identifier(self, request: Request) -> str:
        """Extract user identifier from JWT token if available"""
        try:
            auth_header = request.headers.get('Authorization', '')
            if auth_header.startswith('Bearer '):
                # For now, just use the token as identifier
                # In production, decode JWT to get user ID
                return auth_header[7:50]  # Use first part of token
        except:
            pass
        return None
    
    def check_rate_limit(self, identifier: str, requests_dict: Dict[str, List[float]], 
                        limit: int, window: int, limit_type: str) -> bool:
        """Check if rate limit is exceeded for given identifier"""
        current_time = time.time()
        
        # Clean old requests for this identifier
        requests_dict[identifier] = [
            req_time for req_time in requests_dict[identifier]
            if current_time - req_time < window
        ]
        
        # Check limit
        if len(requests_dict[identifier]) >= limit:
            logger.warning(f"Rate limit exceeded for {limit_type}: {identifier}")
            return False
        
        # Add current request
        requests_dict[identifier].append(current_time)
        return True
    
    async def dispatch(self, request: Request, call_next):
        """Process request with multiple rate limiting strategies"""
        
        # Skip rate limiting for health checks and static files
        exempt_paths = {'/health', '/docs', '/openapi.json', '/'}
        if request.url.path in exempt_paths:
            return await call_next(request)
        
        current_time = time.time()
        client_ip = self.get_client_identifier(request)
        user_id = self.get_user_identifier(request)
        endpoint = f"{request.method}:{request.url.path}"
        
        # Check IP-based rate limit (more permissive)
        if not self.check_rate_limit(
            client_ip, 
            self.ip_requests, 
            settings.RATE_LIMIT_REQUESTS * 2,  # Double limit for IP
            settings.RATE_LIMIT_WINDOW,
            "IP"
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded for IP address",
                headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
            )
        
        # Check user-based rate limit (if authenticated)
        if user_id and not self.check_rate_limit(
            user_id,
            self.user_requests,
            settings.RATE_LIMIT_REQUESTS,
            settings.RATE_LIMIT_WINDOW,
            "User"
        ):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded for user",
                headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
            )
        
        # Check endpoint-specific rate limits for sensitive operations
        sensitive_endpoints = {
            'POST:/api/keywords/upload',
            'POST:/api/blogs/generate', 
            'POST:/api/auth/register',
            'POST:/api/auth/login'
        }
        
        if endpoint in sensitive_endpoints:
            endpoint_limit = settings.RATE_LIMIT_REQUESTS // 4  # Stricter limit
            if not self.check_rate_limit(
                f"{client_ip}:{endpoint}",
                self.endpoint_requests,
                endpoint_limit,
                settings.RATE_LIMIT_WINDOW,
                "Endpoint"
            ):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=f"Rate limit exceeded for {endpoint}",
                    headers={"Retry-After": str(settings.RATE_LIMIT_WINDOW)}
                )
        
        # Process the request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = max(0, settings.RATE_LIMIT_REQUESTS - len(self.ip_requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(settings.RATE_LIMIT_REQUESTS)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + settings.RATE_LIMIT_WINDOW))
        
        return response