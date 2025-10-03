# ============================================================================
# HUMAN HANDOFF SERVICE (handoff/main.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import json

app_handoff = FastAPI(title="Human Handoff Service")

class EscalationRequest(BaseModel):
    user_id: str
    session_id: str
    message: str
    context: Dict[str, Any]

# Mock escalation queue
escalation_queue = []

@app_handoff.post("/escalate")
async def escalate_to_human(request: EscalationRequest):
    escalation = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": request.user_id,
        "session_id": request.session_id,
        "message": request.message,
        "context": request.context,
        "status": "pending"
    }
    escalation_queue.append(escalation)
    
    # In production, publish to Kafka topic
    # kafka_producer.send('escalation_queue', json.dumps(escalation))
    
    return {"status": "escalated", "queue_position": len(escalation_queue)}

@app_handoff.get("/queue")
async def get_queue():
    return {"queue": escalation_queue}

@app_handoff.get("/health")
async def health():
    return {"status": "healthy", "service": "handoff"}