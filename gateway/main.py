# ============================================================================
# API GATEWAY SERVICE (gateway/main.py)
# ============================================================================
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import httpx
import time
import redis
from datetime import datetime, timedelta
import jwt

app = FastAPI(title="API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Redis for rate limiting
redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

SECRET_KEY = "your-secret-key-change-in-production"

class ChatMessage(BaseModel):
    message: str
    user_id: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = {}

class AuthToken(BaseModel):
    token: str

# Rate limiting
async def check_rate_limit(user_id: str):
    key = f"rate_limit:{user_id}"
    count = redis_client.get(key)
    
    if count is None:
        redis_client.setex(key, 60, 1)
        return True
    
    if int(count) >= 60:  # 60 requests per minute
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    redis_client.incr(key)
    return True

# Authentication
def verify_token(authorization: str = Header(None)):
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

@app.post("/api/chat")
async def chat_endpoint(
    message: ChatMessage,
    user: dict = Depends(verify_token)
):
    await check_rate_limit(message.user_id)
    
    # Route to NLU service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://nlu-service:8001/process",
            json={
                "message": message.message,
                "user_id": message.user_id,
                "session_id": message.session_id,
                "metadata": message.metadata
            },
            timeout=30.0
        )
        return response.json()

@app.post("/api/auth/login")
async def login(user_id: str, password: str):
    # Simplified auth - replace with real authentication
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return {"token": token}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "gateway"}