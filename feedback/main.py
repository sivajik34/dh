# ============================================================================
# FEEDBACK SERVICE (feedback/main.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import psycopg2

app = FastAPI(title="Feedback Service")

class Feedback(BaseModel):
    session_id: str
    user_id: str
    rating: int  # 1-5
    comment: Optional[str] = None
    category: Optional[str] = None

def get_db_connection():
    return psycopg2.connect(
        host="postgres",
        database="chatbot_db",
        user="chatbot_user",
        password="chatbot_password"
    )

@app.post("/feedback")
async def submit_feedback(feedback: Feedback):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        """
        INSERT INTO feedback (session_id, user_id, rating, comment, category, created_at)
        VALUES (%s, %s, %s, %s, %s, NOW())
        """,
        (feedback.session_id, feedback.user_id, feedback.rating, 
         feedback.comment, feedback.category)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"status": "success", "message": "Thank you for your feedback!"}

@app.get("/feedback/stats")
async def get_feedback_stats():
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            AVG(rating) as avg_rating,
            COUNT(*) as total_feedback,
            COUNT(CASE WHEN rating >= 4 THEN 1 END) as positive_feedback
        FROM feedback
        WHERE created_at >= NOW() - INTERVAL '7 days'
    """)
    
    stats = cur.fetchone()
    cur.close()
    conn.close()
    
    return {
        "average_rating": float(stats[0]) if stats[0] else 0,
        "total_feedback": stats[1],
        "positive_feedback": stats[2],
        "satisfaction_rate": (stats[2] / stats[1] * 100) if stats[1] > 0 else 0
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "feedback"}