# ============================================================================
# RATE LIMITING MIDDLEWARE (middleware/rate_limiter.py)
# ============================================================================
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import redis
import time

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, redis_client: redis.Redis, max_requests: int = 100, window: int = 60):
        super().__init__(app)
        self.redis = redis_client
        self.max_requests = max_requests
        self.window = window
    
    async def dispatch(self, request: Request, call_next):
        # Extract user identifier
        user_id = request.headers.get("X-User-ID", request.client.host)
        key = f"rate_limit:{user_id}"
        
        # Get current count
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window)
        results = pipe.execute()
        
        current_count = results[0]
        
        # Check limit
        if current_count > self.max_requests:
            raise HTTPException(
                status_code=429,
                detail={
                    "error": "Rate limit exceeded",
                    "retry_after": self.window
                }
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(max(0, self.max_requests - current_count))
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.window)
        
        return response
