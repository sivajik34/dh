# ============================================================================
# LLM ORCHESTRATOR SERVICE (llm/main.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import faiss
import numpy as np
import httpx
from sentence_transformers import SentenceTransformer
# Import strategy factory
from LLMStrategies.factory import get_llm_strategy

# Initialize app
app = FastAPI(title="LLM Orchestrator Service")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
LLM_SERVICE = "azure_openai"  # could be "gemini", "llama", etc.
LLM_CONFIG = {
    "temperature": 0.3,
    "model": "gpt-4o-mini",
    "max_tokens": 3000
}

app = FastAPI(title="LLM Orchestrator Service")

# Vector store for RAG
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
dimension = 384
index = faiss.IndexFlatL2(dimension)


KNOWLEDGE_INGESTION_URL = "http://knowledge-ingestion-service:8011"

async def retrieve_context(query: str, k: int = 3) -> list[str]:
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{KNOWLEDGE_INGESTION_URL}/search",
            params={"k": k},
            json={"query": query}
        )
        data = resp.json()
    return [doc["content"] for doc in data.get("results", [])]

# Knowledge base (in production, load from database)
knowledge_base = [
    "Our return policy allows returns within 30 days of delivery.",
    "Shipping typically takes 3-5 business days for standard delivery.",
    "You can track your order using the tracking ID sent to your email.",
    "Refunds are processed within 5-7 business days after approval.",
]

# Embed and store knowledge
knowledge_embeddings = embedding_model.encode(knowledge_base)
index.add(np.array(knowledge_embeddings).astype('float32'))

class LLMRequest(BaseModel):
    message: str
    context: Dict[str, Any]
    intent: str
    entities: List[Dict[str, Any]]

def retrieve_context_old(query: str, k: int = 3) -> List[str]:
    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(np.array(query_embedding).astype('float32'), k)
    return [knowledge_base[i] for i in indices[0]]

def build_prompt(message: str, context: Dict, retrieved_docs: List[str]) -> str:
    user_profile = context.get('user_profile', {})
    conversation = context.get('conversation_history', {}).get('messages', [])
    
    recent_conversation = "\n".join([
        f"User: {msg.get('message', '')}\nBot: {msg.get('response', '')}"
        for msg in conversation[-3:]
    ])
    
    retrieved_context = "\n".join(retrieved_docs)
    
    prompt = f"""You are a helpful customer service assistant for an e-commerce platform.

User Profile:
- Name: {user_profile.get('name', 'Customer')}
- Tier: {user_profile.get('tier', 'standard')}

Recent Conversation:
{recent_conversation}

Relevant Knowledge:
{retrieved_context}

Current User Message: {message}

Provide a helpful, friendly, and accurate response. If you need more information, ask clarifying questions.
Keep responses concise (2-3 sentences max).

Response:"""
    
    return prompt

@app.post("/generate")
async def generate_response(request: LLMRequest):
    # Retrieve relevant context
    retrieved_docs = await retrieve_context(request.message)
    
    # Build prompt with guardrails
    prompt = build_prompt(request.message, request.context, retrieved_docs)
    llm_strategy = get_llm_strategy(LLM_SERVICE, LLM_CONFIG)
    llm = llm_strategy.initialize()
    # Call LLM API (VertexAI, OpenAI, etc.)
    # For this example, using a mock response
    # In production, integrate with actual LLM endpoint
    
    # Mock LLM call
    #llm_response = f"Based on your inquiry about '{request.intent}', I can help you with that. "

    response = llm.invoke(prompt)
    llm_response = response.content if hasattr(response, "content") else str(response)
    
    if request.intent == "order_status":
        llm_response += "Please provide your order ID so I can check the status for you."
    elif request.intent == "refund_request":
        llm_response += "I'll help you process a refund. Can you share your order details?"
    else:
        llm_response += "How can I assist you further?"
    
    # Validate response
    validation_result = validate_response(llm_response, request.message)
    
    if not validation_result['valid']:
        llm_response = "I apologize, but I need to clarify some details. Could you rephrase your question?"
    
    return {
        "response": llm_response,
        "confidence": validation_result.get('confidence', 0.8),
        "sources": retrieved_docs
    }

def validate_response(response: str, original_message: str) -> Dict:
    # Business rules validation
    forbidden_words = ['guarantee', 'promise', 'definitely will']
    
    if any(word in response.lower() for word in forbidden_words):
        return {'valid': False, 'reason': 'Contains forbidden promises'}
    
    # Length check
    if len(response) > 500:
        return {'valid': False, 'reason': 'Response too long'}
    
    return {'valid': True, 'confidence': 0.85}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "llm_service"}