from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel
from core import final_detect, qwen_chat
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

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

    if result.get("agent_active", False):
        reply = qwen_chat(session_id, text)
    else:
        reply = None

    result["agent_reply"] = reply
    return result

# ======= 🔥 GUVI-FRIENDLY ENDPOINT 🔥 =======
@app.post("/chat")
async def chat(request: Request, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    body = await request.json()

    # Accept ANY shape from GUVI
    text = (
        body.get("text") or
        body.get("message") or
        body.get("input") or
        ""
    )

    session_id = body.get("session_id") or "guvi_session"

    if not text:
        return {"reply": "Hi! Please send a message."}

    reply = qwen_chat(session_id, text)

    return {
        "session_id": session_id,
        "reply": reply
    }
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
