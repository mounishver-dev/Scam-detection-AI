from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from core import final_detect, qwen_chat

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI(title="Scam Detection & Honeypot API")

# In-memory chat memory per session
chat_sessions = {}

class Message(BaseModel):
    session_id: str | None = None
    text: str | None = None


def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


@app.get("/")
def home():
    return {
        "status": "Scam Detection API Running",
        "message": "Use /chat for honeypot interaction and /detect for classification"
    }


@app.post("/detect")
async def detect(request: Request, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    try:
        body = await request.json()
    except:
        body = {}

    session_id = body.get("session_id", "guvi_session")
    text = body.get("text", "")

    if not text:
        return {
            "error": "No text provided",
            "session_id": session_id
        }

    result = final_detect(session_id, text)

    # If scam detected, immediately activate agent and get reply
    agent_reply = None
    if result["agent_active"]:
        try:
            agent_reply = qwen_chat(session_id, text)
        except Exception as e:
            print("AGENT ERROR:", e)
            agent_reply = "Hmm net slow, which bank?"

    result["agent_reply"] = agent_reply
    return result


@app.post("/chat")
async def chat(request: Request, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    # GUVI sometimes sends empty or weird body → handle safely
    try:
        body = await request.json()
    except:
        body = {}

    text = body.get("text", "Hello")
    session_id = body.get("session_id", "guvi_session")

    if session_id not in chat_sessions:
        chat_sessions[session_id] = []

    chat_sessions[session_id].append(f"Scammer: {text}")

    try:
        reply = qwen_chat(session_id, text)
    except Exception as e:
        print("CHAT ERROR:", e)
        reply = "Hmm net slow, which bank?"

    chat_sessions[session_id].append(f"You: {reply}")

    return {
        "session_id": session_id,
        "reply": reply,
        "history": chat_sessions[session_id][-6:]
    }
