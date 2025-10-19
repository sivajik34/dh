# ============================================================================
# CONTEXT SERVICES (context/user_profile_service.py)
# ============================================================================
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import json

app = FastAPI(title="User Profile Service")

class UserProfile(BaseModel):
    user_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = {}
    tier: Optional[str] = "standard"

def get_db_connection():
    return psycopg2.connect(
        host="postgres",
        database="chatbot_db",
        user="chatbot_user",
        password="chatbot_password"
    )

@app.post("/profile")
async def create_profile(profile: UserProfile):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute(
        """
        INSERT INTO user_profiles (user_id, name, email, phone, preferences, tier)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (user_id) DO UPDATE SET
            name = EXCLUDED.name,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            preferences = EXCLUDED.preferences,
            tier = EXCLUDED.tier
        """,
        (profile.user_id, profile.name, profile.email, profile.phone, 
         json.dumps(profile.preferences), profile.tier)
    )
    
    conn.commit()
    cur.close()
    conn.close()
    
    return {"status": "success"}

@app.get("/profile/{user_id}")
async def get_profile(user_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute(
        "SELECT * FROM user_profiles WHERE user_id = %s",
        (user_id,)
    )
    
    profile = cur.fetchone()
    cur.close()
    conn.close()
    
    if profile:
        profile['preferences'] = profile.get('preferences') or {}
        return profile
    return {"error": "Profile not found"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "user_profile"}