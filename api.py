from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
import os
from dotenv import load_dotenv
from core import final_detect, qwen_chat

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

class Message(BaseModel):
    session_id: str | None = None
    text: str

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}

@app.post("/detect")
async def detect(data: Message, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    session_id = data.session_id or "default_session"
    text = data.text

    result = final_detect(session_id, text)

    reply = None
    if result["agent_active"]:
        reply = qwen_chat(session_id, text)

    result["agent_reply"] = reply
    return result

@app.post("/chat")
async def chat(data: Message, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    session_id = data.session_id or "default_session"
    text = data.text

    reply = qwen_chat(session_id, text)

    return {
        "session_id": session_id,
        "reply": reply
    }
