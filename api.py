from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv

from core import final_detect, qwen_chat

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

# 🔹 Store chat history PER SESSION
chat_sessions = {}

class Message(BaseModel):
    session_id: str | None = None
    text: str | None = None

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}

@app.post("/detect")
def detect(data: Message, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    session_id = data.session_id or "default_session"
    text = data.text or ""

    result = final_detect(session_id, text)

    reply = None
    if result.get("agent_active"):
        reply = qwen_chat(session_id, text)

    return {
        "session_id": session_id,
        "text": text,
        "result": result,
        "agent_reply": reply
    }

# 🔹 MAIN HONEYPOT ENDPOINT FOR GUVI
@app.post("/chat")
async def chat(request: Request, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    body = await request.json()
    text = body.get("text") or body.get("message") or ""
    session_id = body.get("session_id") or "guvi_session"

    # Initialize chat history if new session
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    # Add scammer message to history
    chat_sessions[session_id].append(f"Scammer: {text}")

    # Generate reply using YOUR LLM chat logic
    try:
        history_text = "\n".join(chat_sessions[session_id][-8:])
        reply = qwen_chat(session_id, text)
    except Exception as e:
        reply = "Hmm, app issue. One minute."

    # Store bot reply
    chat_sessions[session_id].append(f"You: {reply}")

    return {
        "session_id": session_id,
        "reply": reply,
        "history": chat_sessions[session_id][-6:]
    }
