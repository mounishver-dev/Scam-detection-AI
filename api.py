from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from core import final_detect, qwen_chat, sessions

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

chat_sessions = {}

class Message(BaseModel):
    session_id: str | None = None
    text: str

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}

@app.post("/chat")
async def chat(request: Request, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    body = await request.json()
    text = body.get("text", "")
    session_id = body.get("session_id", "guvi_session")

    # Run detection first (this also updates intelligence in core.py)
    detect_result = final_detect(session_id, text)

    # Get agent reply
    try:
        reply = qwen_chat(session_id, text)
    except Exception:
        reply = "Hmm net slow, which bank?"

    # Get latest session state from core.py
    session_data = sessions.get(session_id, {})

    return {
        "session_id": session_id,
        "reply": reply,
        "scam_detected": detect_result["scam_detected"],
        "agent_active": detect_result["agent_active"],
        "agent_stage": detect_result["agent_stage"],
        "collected_intelligence": detect_result["intelligence"],
        "metrics": detect_result["metrics"],
        "recent_history": session_data.get("history", [])[-6:]
    }
