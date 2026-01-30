import pickle
from rules.rules import rule_detect
from logger import save_log
from llm import llama_detect, qwen_chat as qwen_chat_cloud

model = pickle.load(open("MLmodel/spam_model.pkl", "rb"))
vectorizer = pickle.load(open("MLmodel/vectorizer.pkl", "rb"))

print("Scam Detection System Ready")

chat_history = []
chat_mode = False


def ml_detect(text):
    vec = vectorizer.transform([text])
    prob = model.predict_proba(vec)[0][1]
    print("ML Scam Probability:", round(prob, 3))
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
    return final_result, rule_result, ml_result, llama_result, qwen_result


if __name__ == "__main__":
    while True:
        text = input("\nEnter message (or type exit): ")

        if text.lower() == "exit":
            break

        if chat_mode:
            reply = qwen_chat(text)
            print("\nQwen Reply:", reply)
            continue

        final_result, rule_r, ml_r, llama_r, qwen_r = final_detect(text)

        print("\n--- Detection Results ---")
        print("Rules Engine:", rule_r)
        print("ML Model:", ml_r)
        print("Llama AI:", llama_r)
        print("Qwen AI:", qwen_r)
        print("FINAL RESULT:", final_result)

        results = {
            "rules": rule_r,
            "ml": ml_r,
            "llama": llama_r,
            "qwen": qwen_r,
            "final": final_result
        }

        save_log(text, results, chat_history)

        if final_result == "SPAM":
            chat_mode = True
            print("\nScam detected! AI chat started automatically.")
            reply = qwen_chat(text)
            print("\nQwen Reply:", reply)
