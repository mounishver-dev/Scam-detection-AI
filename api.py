from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from core import final_detect, qwen_chat

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

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    chat_sessions[session_id].append(f"Scammer: {text}")

    try:
        reply = qwen_chat(session_id, text)
    except Exception:
        reply = "Hmm net slow, which bank?"

    chat_sessions[session_id].append(f"You: {reply}")

    return {
        "session_id": session_id,
        "reply": reply,
        "history": chat_sessions[session_id][-6:]
    }
