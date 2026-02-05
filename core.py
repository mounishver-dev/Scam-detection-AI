import pickle
import time
import re
from rules.rules import rule_detect
from logger import save_log
from llm import llama_detect, qwen_chat as qwen_chat_cloud

# =========================
# INTELLIGENCE EXTRACTION
# =========================
def extract_intel(text):
    return {
        "upi_ids": re.findall(r"\b[\w.-]+@[\w.-]+\b", text),
        "bank_accounts": re.findall(r"\b\d{9,18}\b", text),
        "ifsc_codes": re.findall(r"\b[A-Z]{4}0[A-Z0-9]{6}\b", text),
        "urls": re.findall(r"https?://\S+", text),
        "phone_numbers": re.findall(r"\b\d{10}\b", text)
    }

# =========================
# SESSION STORE
# =========================
sessions = {}

def init_session(session_id):
    if session_id not in sessions:
        sessions[session_id] = {
            "history": [],
            "agent_active": False,
            "start_time": time.time(),
            "intelligence": {
                "upi_ids": [],
                "bank_accounts": [],
                "ifsc_codes": [],
                "urls": [],
                "phone_numbers": []
            }
        }

# =========================
# LOAD ML MODEL
# =========================
model = pickle.load(open("MLmodel/spam_model.pkl", "rb"))
vectorizer = pickle.load(open("MLmodel/vectorizer.pkl", "rb"))

def ml_detect(text):
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    return "SPAM" if prob > 0.25 else "SAFE"

def qwen_detect(text):
    return llama_detect(text)

# =========================
# 🔥 MAIN CHAT FUNCTION (FIXED)
# =========================
def qwen_chat(session_id, scammer_message):
    init_session(session_id)

    history = sessions[session_id]["history"]

    # Store scammer message
    history.append(f"Scammer: {scammer_message}")

    # Extract intelligence
    intel = extract_intel(scammer_message)
    for key in intel:
        sessions[session_id]["intelligence"][key].extend(intel[key])

    # Build history for LLM (last 8 turns)
    history_text = "\n".join(history[-8:])

    # 🔥 ALWAYS CALL QWEN (FROM TURN 1)
    reply = qwen_chat_cloud(scammer_message, history_text)

    # Store bot reply
    history.append(f"You: {reply}")

    save_log(scammer_message, {"mode": "chat"}, history)

    return reply

# =========================
# FINAL DETECTION PIPELINE
# =========================
def final_detect(session_id, text):
    init_session(session_id)

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

    # Extract intelligence
    intel = extract_intel(text)
    for key in intel:
        sessions[session_id]["intelligence"][key].extend(intel[key])

    # Activate agent if spam detected
    if final_result == "SPAM":
        sessions[session_id]["agent_active"] = True

    # Metrics
    duration = round(time.time() - sessions[session_id]["start_time"], 2)

    return {
        "scam_detected": final_result == "SPAM",
        "final_label": final_result,
        "agent_active": sessions[session_id]["agent_active"],
        "session_id": session_id,
        "duration_sec": duration,
        "intelligence": sessions[session_id]["intelligence"]
    }
