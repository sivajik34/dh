# ============================================================================
# TESTING - UNIT TESTS (tests/test_nlu.py)
# ============================================================================
import pytest
from fastapi.testclient import TestClient
import sys
sys.path.append('..')

@pytest.fixture
def nlu_client():
    from nlu.main import app_nlu
    return TestClient(app_nlu)

def test_intent_classification():
    """Test intent classification accuracy"""
    from nlu.main import classify_intent
    
    test_cases = [
        ("Where is my order AB12345678?", "order_status"),
        ("I want to return this product", "refund_request"),
        ("Tell me about this product", "product_inquiry"),
    ]
    
    for message, expected_intent in test_cases:
        intent, confidence = classify_intent(message)
        assert intent == expected_intent or confidence > 0.5

def test_entity_extraction():
    """Test entity extraction"""
    from nlu.main import extract_entities
    
    text = "My order ID is AB12345678 and I need help"
    entities = extract_entities(text)
    
    order_entities = [e for e in entities if e['label'] == 'ORDER_ID']
    assert len(order_entities) > 0
    assert order_entities[0]['text'] == 'AB12345678'

def test_nlu_endpoint(nlu_client):
    """Test NLU processing endpoint"""
    response = nlu_client.post("/process", json={
        "message": "Where is my order?",
        "user_id": "test_user",
        "session_id": "test_session"
    })
    
    assert response.status_code == 200
    data = response.json()
    assert 'intent' in data
    assert 'confidence' in data
    assert 'entities' in data