from fastapi import FastAPI
from pydantic import BaseModel
from main import final_detect, qwen_chat, chat_history

app = FastAPI()

class Message(BaseModel):
    text: str

@app.post("/detect")
def detect_message(data: Message):
    text = data.text

    final_result, rule_r, ml_r, llama_r, qwen_r = final_detect(text)

    response = {
        "text": text,
        "rules": rule_r,
        "ml": ml_r,
        "llm_llama": llama_r,
        "llm_qwen": qwen_r,
        "final_result": final_result
    }

    return response


@app.post("/chat")
def chat_with_scammer(data: Message):
    text = data.text
    reply = qwen_chat(text, "\n".join(chat_history))
    
    return {
        "scammer_message": text,
        "ai_reply": reply
    }
