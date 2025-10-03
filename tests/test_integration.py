# ============================================================================
# TESTING - INTEGRATION TESTS (tests/test_integration.py)
# ============================================================================
import pytest
import asyncio
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_full_conversation_flow():
    """Test complete conversation flow from gateway to response"""
    async with AsyncClient(base_url="http://gateway:8000") as client:
        # Login
        login_response = await client.post("/api/auth/login", json={
            "user_id": "test_user",
            "password": "test_password"
        })
        assert login_response.status_code == 200
        token = login_response.json()['token']
        
        # Send chat message
        chat_response = await client.post(
            "/api/chat",
            json={
                "message": "Where is my order AB12345678?",
                "user_id": "test_user",
                "session_id": "test_session"
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert chat_response.status_code == 200
        response_data = chat_response.json()
        assert 'response' in response_data

@pytest.mark.asyncio
async def test_rate_limiting():
    """Test rate limiting functionality"""
    async with AsyncClient(base_url="http://gateway:8000") as client:
        # Send multiple requests
        responses = []
        for i in range(65):
            response = await client.post("/api/chat", json={
                "message": f"Test message {i}",
                "user_id": "test_user",
                "session_id": "test_session"
            })
            responses.append(response)
        
        # Check that rate limiting kicked in
        rate_limited = [r for r in responses if r.status_code == 429]
        assert len(rate_limited) > 0