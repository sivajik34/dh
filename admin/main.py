# ============================================================================
# ADMIN DASHBOARD BACKEND (admin/main.py)
# ============================================================================
from fastapi import FastAPI, Depends
from typing import List, Dict
import psycopg2
from datetime import datetime, timedelta

app = FastAPI(title="Admin Dashboard API")

@app.get("/dashboard/overview")
async def get_overview():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get key metrics
    cur.execute("""
        SELECT 
            (SELECT COUNT(*) FROM escalations WHERE status = 'pending') as pending_escalations,
            (SELECT COUNT(DISTINCT session_id) FROM audit_logs 
             WHERE timestamp >= NOW() - INTERVAL '24 hours') as active_sessions_24h,
            (SELECT AVG(rating) FROM feedback 
             WHERE created_at >= NOW() - INTERVAL '7 days') as avg_rating_7d,
            (SELECT COUNT(*) FROM orders 
             WHERE created_at >= NOW() - INTERVAL '24 hours') as orders_24h
    """)
    
    metrics = cur.fetchone()
    cur.close()
    conn.close()
    
    return {
        "pending_escalations": metrics[0],
        "active_sessions_24h": metrics[1],
        "average_rating_7d": float(metrics[2]) if metrics[2] else 0,
        "orders_24h": metrics[3],
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/dashboard/intents")
async def get_intent_distribution():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            details->>'intent' as intent,
            COUNT(*) as count
        FROM audit_logs
        WHERE action = 'intent_classified'
        AND timestamp >= NOW() - INTERVAL '7 days'
        GROUP BY details->>'intent'
        ORDER BY count DESC
        LIMIT 10
    """)
    
    intents = cur.fetchall()
    cur.close()
    conn.close()
    
    return {
        "intents": [
            {"intent": row[0], "count": row[1]} 
            for row in intents
        ]
    }

@app.get("/dashboard/performance")
async def get_performance_metrics():
    return {
        "avg_response_time_ms": 250,
        "success_rate": 0.95,
        "llm_usage_percent": 35,
        "escalation_rate": 0.08
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "admin"}