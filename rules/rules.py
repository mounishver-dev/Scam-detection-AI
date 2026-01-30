import re

SCAM_KEYWORDS = [
    "blocked", "block", "hacked", "hack", "otp", "urgent", "verify",
    "upi", "send", "money", "rs", "amount", "bank", "account", "card",
    "important", "limited", "claim", "password", "transfer", "pay"
]

UPI_PATTERN = r"\b[\w.-]+@[\w.-]+\b|\bupi\b"
MONEY_PATTERN = r"\b\d+\s?(rs|inr|rupees)\b"
URL_PATTERN = r"(https?://\S+|www\.\S+)"

def rule_score(text):
    text = text.lower()
    score = 0

    for word in SCAM_KEYWORDS:
        if word in text:
            score += 1

    if re.search(UPI_PATTERN, text):
        score += 3

    if re.search(MONEY_PATTERN, text):
        score += 2

    if re.search(URL_PATTERN, text):
        score += 2

    return score

def rule_detect(text):
    score = rule_score(text)
    return "SPAM" if score >= 2 else "SAFE"
