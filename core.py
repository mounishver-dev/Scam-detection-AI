import pickle
from rules.rules import rule_detect
from logger import save_log
from llm import llama_detect, qwen_chat as qwen_chat_cloud

model = pickle.load(open("MLmodel/spam_model.pkl", "rb"))
vectorizer = pickle.load(open("MLmodel/vectorizer.pkl", "rb"))

chat_history = []

def ml_detect(text):
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    return "SPAM" if prob > 0.25 else "SAFE"

def qwen_detect(text):
    return llama_detect(text)

def qwen_chat(scammer_message):
    global chat_history

    chat_history.append(f"Scammer: {scammer_message}")
    history_text = "\n".join(chat_history[-8:])

    reply = qwen_chat_cloud(scammer_message, history_text)
    chat_history.append(f"You: {reply}")
    save_log(scammer_message, {"mode": "chat"}, chat_history)

    return reply

def final_detect(text):
    rule_result = rule_detect(text)
    ml_result = ml_detect(text)
    llama_result = llama_detect(text)
    qwen_result = qwen_detect(text)

    score = 0
    if rule_result == "SPAM":
        score += 1
    if ml_result == "SPAM":
        score += 1
    if llama_result == "SPAM":
        score += 2
    if qwen_result == "SPAM":
        score += 2

    final_result = "SPAM" if score >= 3 else "SAFE"

    return {
        "final": final_result,
        "rules": rule_result,
        "ml": ml_result,
        "llama": llama_result,
        "qwen": qwen_result
    }
