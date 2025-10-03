# ============================================================================
# CONVERSATION HISTORY SERVICE (context/conversation_service.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import redis
import json

app_conv = FastAPI(title="Conversation History Service")

redis_client = redis.Redis(host='redis', port=6379, decode_responses=True)

class ConversationMessage(BaseModel):
    session_id: str
    user_id: str
    message: str
    response: str
    timestamp: Optional[str] = None
    intent: Optional[str] = None
    confidence: Optional[float] = None

@app_conv.post("/conversation/add")
async def add_message(conv: ConversationMessage):
    if not conv.timestamp:
        conv.timestamp = datetime.utcnow().isoformat()
    
    key = f"conversation:{conv.session_id}"
    message_data = json.dumps(conv.dict())
    
    redis_client.rpush(key, message_data)
    redis_client.expire(key, 86400)  # 24 hours
    
    return {"status": "success"}

@app_conv.get("/conversation/{session_id}")
async def get_conversation(session_id: str, limit: int = 10):
    key = f"conversation:{session_id}"
    messages = redis_client.lrange(key, -limit, -1)
    
    return {
        "session_id": session_id,
        "messages": [json.loads(msg) for msg in messages]
    }

@app_conv.get("/health")
async def health():
    return {"status": "healthy", "service": "conversation_history"}