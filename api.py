from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv

# Import your core logic
from core import final_detect, qwen_chat  

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI(title="Scam Detection Honeypot API")

class Message(BaseModel):
    session_id: str | None = None
    text: str | None = None

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/")
def home():
    return {
        "status": "online",
        "service": "Scam Detection Honeypot",
        "version": "1.0"
    }

# ----------- DETECTION ENDPOINT -----------
@app.post("/detect")
def detect(data: Message, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    session_id = data.session_id or "default_session"
    text = data.text or ""

    try:
        result = final_detect(session_id, text)
    except Exception as e:
        return {
            "error": "detection_failed",
            "message": str(e)
        }

    # If agent should respond
    agent_reply = None
    if isinstance(result, dict) and result.get("agent_active", False):
        try:
            agent_reply = qwen_chat(session_id, text)
        except:
            agent_reply = "Hmm, network issue."

    return {
        "session_id": session_id,
        "text": text,
        "result": result,
        "agent_reply": agent_reply
    }

# ----------- GUVI HONEYPOT ENDPOINT (MOST IMPORTANT) -----------
@app.post("/chat")
async def chat(request: Request, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    try:
        body = await request.json()
    except:
        body = {}

    # Accept ANY possible field name from GUVI
    text = (
        body.get("text") or
        body.get("message") or
        body.get("input") or
        ""
    )

    session_id = body.get("session_id") or "guvi_session"

    if not text:
        return {
            "session_id": session_id,
            "reply": "Hi, what happened?"
        }

    try:
        reply = qwen_chat(session_id, text)
    except Exception as e:
        reply = "Hmm, app issue. One minute."

    return {
        "session_id": session_id,
        "reply": reply
    }
