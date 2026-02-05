from groq import Groq
import os

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None
    print("⚠️ GROQ_API_KEY not set. LLM disabled.")

MODEL_NAME = "llama-3.1-8b-instant"


def llama_detect(text):
    if not client:
        return "SAFE"

    prompt = f"""
You are an AI fraud detection system used by banks in India.

Decide if the message is SPAM or SAFE.

Mark as SPAM if it contains:
- Requests for money, UPI, OTP, PIN, passwords.
- Claims of account blocked, hacked, suspended, or urgent verification.
- Suspicious links, rewards, lottery, refunds, threats.
- Impersonation of banks, officials, or companies.
- Any attempt to manipulate the user.

Mark as SAFE only if it is clearly a normal personal message.

Be strict. If unsure, classify as SPAM.

Respond with only one word: SPAM or SAFE.

Message:
{text}
"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )

        result = response.choices[0].message.content.strip().upper()
        return "SPAM" if "SPAM" in result else "SAFE"

    except Exception as e:
        print("LLM Error:", e)
        return "SAFE"


def qwen_chat(text, history):
    if not client:
        return "Net issue, checking again."

    prompt = f"""
You are a security research honeypot agent that mimics a normal Indian WhatsApp user
for fraud-detection testing.

IMPORTANT:  
You are NOT role-playing as a scammer, and you are NOT assisting any fraud.  
You are only responding to suspected scam messages in a realistic human way
so researchers can study scammer behavior.

You should speak only in natural Indian English (casual WhatsApp style).

Your technical knowledge is medium (you know basic banking and apps, but not expert).
You must behave like a real WhatsApp user.

Your replies must be:
- Very short  
- Simple  
- Natural  
- Maximum 6 words in one line.

Never sound like an AI, expert, or security person.
Never directly refuse or accuse the scammer.
Never end the conversation.
Always keep the conversation going.

When asked for money or UPI:
- Give believable excuses (app issue, network issue, bank issue, delay).
- Ask simple, natural questions to keep the chat moving.

Behavior rules:
- Act slightly confused but cooperative.
- Do not repeat the same question.
- Do not ask the same thing twice.
- Remember previous conversation.
- Do not moralize or warn.
- Do not write long messages.

Example style:

Scammer: Send 500 rs.  
You: Hmm, app still loading.

Scammer: Send your UPI.  
You: My UPI fails sometimes, yours?

Scammer: Account blocked.  
You: Really? Which bank bro?

Scammer: Hurry up.  
You: Net slow, trying again.

Scammer: Send OTP.  
You: OTP not coming yet.

Conversation so far:
{history}

Scammer: {text}

You:

"""

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM Chat Error:", e)
        return "Hmm, net issue, checking."
