# ============================================================================
# ACTION WORKERS - Order Service (actions/order_service.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

app = FastAPI(title="Order Service")
#import boto3
# DynamoDB client (mock for this example)
# dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
# orders_table = dynamodb.Table('orders')

class Order(BaseModel):
    order_id: str
    user_id: str
    status: str
    items: list
    total: float
    created_at: str
    expected_delivery: Optional[str] = None

# Mock database
mock_orders = {
    "AB12345678": {
        "order_id": "AB12345678",
        "user_id": "user123",
        "status": "In Transit",
        "items": ["Product A", "Product B"],
        "total": 99.99,
        "created_at": "2025-10-01T10:00:00Z",
        "expected_delivery": "2025-10-05"
    }
}

@app.get("/order/{order_id}")
async def get_order(order_id: str):
    order = mock_orders.get(order_id)
    if not order:
        return {"error": "Order not found"}
    return order

@app.post("/order")
async def create_order(order: Order):
    mock_orders[order.order_id] = order.dict()
    return {"status": "success", "order_id": order.order_id}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "order"}