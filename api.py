from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
from core import final_detect, qwen_chat
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

class Message(BaseModel):
    session_id: str
    text: str

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}

@app.post("/detect")
def detect(data: Message, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    result = final_detect(data.session_id, data.text)

    if result.get("agent_active", False):
        reply = qwen_chat(data.session_id, data.text)
    else:
        reply = None

    result["agent_reply"] = reply
    return result

@app.api_route("/chat", methods=["GET", "POST"])
def chat(
    x_api_key: str = Header(None),
    data: Message | None = None,
    text: str | None = None,
    session_id: str | None = None,
):
    verify_api_key(x_api_key)

    if data:
        session_id = data.session_id
        text = data.text

    if not text or not session_id:
        return {"status": "alive"}

    reply = qwen_chat(session_id, text)

    return {
        "session_id": session_id,
        "reply": reply
    }
