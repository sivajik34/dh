# ============================================================================
# ORCHESTRATOR SERVICE (orchestrator/main.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import httpx
from enum import Enum
from middleware.metrics import setup_metrics_endpoint

app = FastAPI(title="Orchestrator Service")

setup_metrics_endpoint(app)

class IntentType(str, Enum):
    ORDER_STATUS = "order_status"
    REFUND_REQUEST = "refund_request"
    PRODUCT_INQUIRY = "product_inquiry"
    COMPLAINT = "complaint"
    SHIPPING_INFO = "shipping_info"
    CANCEL_ORDER = "cancel_order"

class OrchestratorRequest(BaseModel):
    message: str
    user_id: str
    session_id: str
    intent: str
    confidence: float
    entities: List[Dict[str, Any]]
    requires_llm: bool
    context: Dict[str, Any]

async def handle_order_status(entities: List[Dict], context: Dict) -> Dict:
    # Extract order ID
    order_id = None
    for entity in entities:
        if entity['label'] == 'ORDER_ID':
            order_id = entity['text']
            break
    
    if not order_id:
        return {
            "response": "Could you please provide your order ID? It should look like 'AB12345678'.",
            "requires_input": True
        }
    
    # Call order tracking service
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"http://order-service:8005/order/{order_id}",
            timeout=10.0
        )
        order_data = response.json()
    
    if order_data.get('error'):
        return {
            "response": f"I couldn't find an order with ID {order_id}. Please check and try again.",
            "requires_input": True
        }
    
    return {
        "response": f"Your order {order_id} is currently {order_data['status']}. "
                   f"Expected delivery: {order_data.get('expected_delivery', 'TBD')}.",
        "data": order_data
    }

async def handle_refund_request(entities: List[Dict], context: Dict) -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://refund-service:8006/refund/initiate",
            json={"user_id": context.get("user_id"), "entities": entities},
            timeout=10.0
        )
        return response.json()

async def handle_with_llm(request: OrchestratorRequest) -> Dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://llm-service:8007/generate",
            json={
                "message": request.message,
                "context": request.context,
                "intent": request.intent,
                "entities": request.entities
            },
            timeout=60.0
        )
        return response.json()

@app.post("/orchestrate")
async def orchestrate(request: OrchestratorRequest):
    # State machine logic
    if request.requires_llm or request.confidence < 0.7:
        result = await handle_with_llm(request)
    elif request.intent == IntentType.ORDER_STATUS:
        result = await handle_order_status(request.entities, request.context)
    elif request.intent == IntentType.REFUND_REQUEST:
        result = await handle_refund_request(request.entities, request.context)
    else:
        # Default to LLM for complex queries
        result = await handle_with_llm(request)
    
    # Check if human handoff is needed
    escalation_keywords = ['speak to human', 'agent', 'representative', 'manager']
    if any(keyword in request.message.lower() for keyword in escalation_keywords):
        async with httpx.AsyncClient() as client:
            await client.post(
                "http://handoff-service:8008/escalate",
                json={
                    "user_id": request.user_id,
                    "session_id": request.session_id,
                    "message": request.message,
                    "context": request.context
                }
            )
        result['escalated'] = True
        result['response'] = "I'm connecting you with a human agent. Please wait..."
    
    # Store conversation
    async with httpx.AsyncClient() as client:
        await client.post(
            "http://conversation-service:8003/conversation/add",
            json={
                "session_id": request.session_id,
                "user_id": request.user_id,
                "message": request.message,
                "response": result.get('response', ''),
                "intent": request.intent,
                "confidence": request.confidence
            }
        )
    
    return result

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "orchestrator"}