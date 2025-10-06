# ============================================================================
# NLU PIPELINE SERVICE (nlu/main.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import spacy
import httpx
import numpy as np
from middleware.metrics import setup_metrics_endpoint

app = FastAPI(title="NLU Service")

setup_metrics_endpoint(app)

# Load models
nlp = spacy.load("en_core_web_sm")

# Intent classification model (DistilBERT)
intent_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
intent_model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased",
    num_labels=10  # Adjust based on your intents
)

# Intent labels
INTENT_LABELS = [
    "order_status",
    "refund_request",
    "product_inquiry",
    "complaint",
    "account_issue",
    "shipping_info",
    "payment_issue",
    "cancel_order",
    "general_query",
    "other"
]

class NLURequest(BaseModel):
    message: str
    user_id: str
    session_id: str
    metadata: Optional[Dict[str, Any]] = {}

class NLUResponse(BaseModel):
    intent: str
    confidence: float
    entities: List[Dict[str, Any]]
    requires_llm: bool
    orchestrator_response:Optional[Dict[str, Any]] = None

def classify_intent(text: str) -> tuple:
    inputs = intent_tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    
    with torch.no_grad():
        outputs = intent_model(**inputs)
        logits = outputs.logits
        probs = torch.nn.functional.softmax(logits, dim=-1)
        confidence, predicted_class = torch.max(probs, dim=-1)
    
    intent = INTENT_LABELS[predicted_class.item()]
    confidence_score = confidence.item()
    
    return intent, confidence_score

def extract_entities(text: str) -> List[Dict[str, Any]]:
    doc = nlp(text)
    entities = []
    
    for ent in doc.ents:
        entities.append({
            "text": ent.text,
            "label": ent.label_,
            "start": ent.start_char,
            "end": ent.end_char
        })
    
    # Extract custom entities (order IDs, etc.)
    # Simple pattern matching for order IDs
    import re
    order_pattern = r'\b[A-Z]{2}\d{8,10}\b'
    for match in re.finditer(order_pattern, text):
        entities.append({
            "text": match.group(),
            "label": "ORDER_ID",
            "start": match.start(),
            "end": match.end()
        })
    
    return entities

@app.post("/process", response_model=NLUResponse)
async def process_message(request: NLURequest):
    # Classify intent
    intent, confidence = classify_intent(request.message)
    
    # Extract entities
    entities = extract_entities(request.message)
    
    # Determine if LLM is needed
    requires_llm = confidence < 0.7 or intent == "other"
    
    # Get context
    async with httpx.AsyncClient() as client:
        # Fetch user profile
        profile_response = await client.get(
            f"http://user-profile-service:8002/profile/{request.user_id}"
        )
        user_profile = profile_response.json()
        
        # Fetch conversation history
        conv_response = await client.get(
            f"http://conversation-service:8003/conversation/{request.session_id}"
        )
        conversation_history = conv_response.json()
    
    # Route to orchestrator
    orchestrator_request = {
        "message": request.message,
        "user_id": request.user_id,
        "session_id": request.session_id,
        "intent": intent,
        "confidence": confidence,
        "entities": entities,
        "requires_llm": requires_llm,
        "context": {
            "user_profile": user_profile,
            "conversation_history": conversation_history
        }
    }
    
    async with httpx.AsyncClient() as client:
        orchestrator_response = await client.post(
            "http://orchestrator-service:8004/orchestrate",
            json=orchestrator_request,
            timeout=60.0
        )
        orchestrator_data = orchestrator_response.json()
    
    # Map back to NLUResponse
    return NLUResponse(
        intent=intent,
        confidence=confidence,
        entities=entities,
        requires_llm=requires_llm,
        orchestrator_response= orchestrator_data
    )

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "nlu"}