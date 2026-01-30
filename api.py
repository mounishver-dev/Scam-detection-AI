from fastapi import FastAPI
from pydantic import BaseModel
from core import final_detect, qwen_chat
import os
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

app = FastAPI()

class Message(BaseModel):
    session_id: str 
    text: str

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}

@app.post("/detect")
def detect(data: Message, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)

    result = final_detect(data.session_id, data.text)

    if result["agent_active"]:
        reply = qwen_chat(data.session_id, data.text)
    else:
        reply = None

    result["agent_reply"] = reply

    return result




@app.post("/chat")
def chat(data: Message, x_api_key: str = Header(None)):
    verify_api_key(x_api_key)
    reply = qwen_chat(data.session_id, data.text)
    return {"reply": reply}


