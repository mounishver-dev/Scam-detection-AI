from fastapi import FastAPI
from pydantic import BaseModel

from core import final_detect
from llm import qwen_chat

app = FastAPI()

class Message(BaseModel):
    text: str

chat_history = []

@app.post("/detect")
def detect_message(data: Message):
    text = data.text

    final_result, rule_r, ml_r, llama_r, qwen_r = final_detect(text)

    return {
        "text": text,
        "rules": rule_r,
        "ml": ml_r,
        "llm_llama": llama_r,
        "llm_qwen": qwen_r,
        "final_result": final_result
    }

@app.post("/chat")
def chat_with_scammer(data: Message):
    global chat_history

    text = data.text
    history_text = "\n".join(chat_history)

    reply = qwen_chat(text, history_text)

    chat_history.append(f"Scammer: {text}")
    chat_history.append(f"You: {reply}")

    return {
        "reply": reply
    }
