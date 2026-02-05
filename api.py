from fastapi import FastAPI, Header, HTTPException, Request
import os
from dotenv import load_dotenv
from core import qwen_chat

load_dotenv()
API_KEY = os.getenv("API_KEY")  # Must be set on Render as: guvi-honeypot-123

app = FastAPI()

@app.get("/")
def home():
    return {"status": "running"}

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.post("/chat")
async def chat(request: Request, x_api_key: str = Header(None)):

    # 1) Verify API key
    verify_api_key(x_api_key)

    # 2) Read raw body (GUVI sends a different structure)
    body = await request.json()

    # 3) Extract fields from GUVI format
    session_id = body.get("sessionId", "guvi_session")

    message_obj = body.get("message", {})
    text = message_obj.get("text", "")

    if not text:
        return {
            "status": "error",
            "reply": "No message provided"
        }

    # 4) Call your Qwen honeypot agent (core.py)
    try:
        reply = qwen_chat(session_id, text)
    except Exception as e:
        print("LLM ERROR:", e)
        reply = "Hmm net slow, which bank?"

    # 5) RETURN EXACT FORMAT GUVI WANTS
    return {
        "status": "success",
        "reply": reply
    }
