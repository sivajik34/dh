# ============================================================================
# REFUND SERVICE (actions/refund_service.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel

app_refund = FastAPI(title="Refund Service")

class RefundRequest(BaseModel):
    user_id: str
    entities: list

@app_refund.post("/refund/initiate")
async def initiate_refund(request: RefundRequest):
    # Mock refund processing
    return {
        "response": "Your refund request has been initiated. You'll receive an email confirmation shortly.",
        "refund_id": "RF123456",
        "status": "pending_approval"
    }

@app_refund.get("/health")
async def health():
    return {"status": "healthy", "service": "refund"}