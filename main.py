from core import final_detect, qwen_chat

print("Scam Detection System Ready")

chat_mode = False

while True:
    text = input("\nEnter message (or type exit): ")

    if text.lower() == "exit":
        break

    if chat_mode:
        reply, _ = qwen_chat(text)
        print("🤖 Qwen:", reply)
        continue

    result = final_detect(text)

    print("\n--- Detection Results ---")
    for k, v in result.items():
        print(f"{k.upper()}: {v}")

    if result["final"] == "SPAM":
        chat_mode = True
        print("\n⚠️ Scam detected! AI chat started.")

        reply, _ = qwen_chat(text)
        print("🤖 Qwen:", reply)
