import json
import re
from datetime import datetime

LOG_FILE = "scam_logs.json"

def extract_scam_data(text):
    upi_pattern = r"\b[\w.-]+@[\w.-]+\b"
    phone_pattern = r"\b\d{10}\b"
    amount_pattern = r"\b\d+\s?(?:rs|inr)?\b"
    link_pattern = r"https?://\S+"

    upi = re.findall(upi_pattern, text.lower())
    phone = re.findall(phone_pattern, text)
    amount = re.findall(amount_pattern, text.lower())
    link = re.findall(link_pattern, text)

    return {
        "upi": upi[0] if upi else None,
        "phone": phone[0] if phone else None,
        "amount": amount[0] if amount else None,
        "link": link[0] if link else None
    }

def save_log(message, results, chat_history):
    log_entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "message": message,
        "detection": results,
        "scammer_data": extract_scam_data(message),
        "chat_history": chat_history[-10:]
    }

    try:
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    except:
        logs = []

    logs.append(log_entry)

    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, indent=4)
