# ============================================================================
# TESTING - LOAD TESTS (tests/load_test.py)
# ============================================================================
# Run with: locust -f tests/load_test.py --host=http://localhost:8000
from locust import HttpUser, task, between
import random

class ChatbotUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        """Login before starting tests"""
        response = self.client.post("/api/auth/login", json={
            "user_id": f"user_{random.randint(1, 1000)}",
            "password": "test_password"
        })
        self.token = response.json()['token']
        self.session_id = f"session_{random.randint(1, 10000)}"
    
    @task(3)
    def send_order_status_query(self):
        """Test order status queries"""
        self.client.post(
            "/api/chat",
            json={
                "message": "Where is my order AB12345678?",
                "user_id": f"user_{random.randint(1, 1000)}",
                "session_id": self.session_id
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(2)
    def send_refund_query(self):
        """Test refund queries"""
        self.client.post(
            "/api/chat",
            json={
                "message": "I want to return my order",
                "user_id": f"user_{random.randint(1, 1000)}",
                "session_id": self.session_id
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )
    
    @task(1)
    def send_general_query(self):
        """Test general queries"""
        queries = [
            "How do I track my order?",
            "What is your return policy?",
            "Do you offer international shipping?",
            "How can I contact support?"
        ]
        self.client.post(
            "/api/chat",
            json={
                "message": random.choice(queries),
                "user_id": f"user_{random.randint(1, 1000)}",
                "session_id": self.session_id
            },
            headers={"Authorization": f"Bearer {self.token}"}
        )