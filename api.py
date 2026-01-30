from fastapi import FastAPI
from pydantic import BaseModel
from core import final_detect, qwen_chat

app = FastAPI()

class Message(BaseModel):
    text: str

@app.get("/")
def home():
    return {"status": "Scam Detection API Running"}

@app.post("/detect")
def detect(data: Message):
    return final_detect(data.text)

@app.post("/chat")
def chat(data: Message):
    reply = qwen_chat(data.text)
    return {
        "reply": reply
    }

