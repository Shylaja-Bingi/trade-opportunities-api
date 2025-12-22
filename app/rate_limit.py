from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta
from collections import defaultdict
from app.config import settings

# Simple in-memory rate limiter
class RateLimiter:
    def __init__(self):
        self.requests = defaultdict(list)
    
    def is_rate_limited(self, key: str) -> bool:
        """Check if user has exceeded rate limit"""
        now = datetime.now()
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] 
                             if now - req_time < timedelta(seconds=settings.rate_limit_period)]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= settings.rate_limit_requests:
            return True
        
        # Add current request
        self.requests[key].append(now)
        return False

rate_limiter = RateLimiter()

def check_rate_limit(request: Request, user_identifier: str):
    """Middleware to check rate limit"""
    if rate_limiter.is_rate_limited(user_identifier):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {settings.rate_limit_period} seconds.",
            headers={"Retry-After": str(settings.rate_limit_period)}
        )