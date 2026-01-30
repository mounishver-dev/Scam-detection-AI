import pickle
from rules import rule_detect
from llm import llama_detect

model = pickle.load(open("MLmodel/spam_model.pkl", "rb"))
vectorizer = pickle.load(open("MLmodel/vectorizer.pkl", "rb"))

def ml_detect(text):
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    return "SPAM" if prob > 0.25 else "SAFE"

def final_detect(text):
    rule_r = rule_detect(text)
    ml_r = ml_detect(text)
    llama_r = llama_detect(text)
    qwen_r = llama_r  # optional

    score = 0
    if rule_r == "SPAM": score += 1
    if ml_r == "SPAM": score += 1
    if llama_r == "SPAM": score += 2
    if qwen_r == "SPAM": score += 2

    final_result = "SPAM" if score >= 3 else "SAFE"

    return final_result, rule_r, ml_r, llama_r, qwen_r
