# main.py (ONLY for local testing)

if __name__ == "__main__":
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

        print(result)

        if result["final"] == "SPAM":
            chat_mode = True
            reply, _ = qwen_chat(text)
            print("🤖 Qwen:", reply)
