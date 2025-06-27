from flask import Flask, request
import requests
import os

app = Flask(__name__)

GROUPME_BOT_ID = os.getenv("GROUPME_BOT_ID")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

@app.route('/')
def home():
    return 'GreggBot is running.', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Webhook was called")
    print("Incoming data:", data)

    message = data.get("text", "").lower()
    sender = data.get("name", "")

    if sender.lower() == "greggbot":
        return '', 200

    if "greggbot" not in message and "itzaroni" not in message:
        return '', 200  # Ignore unrelated messages

    # Prompt for sarcasm
    prompt = (
        "You are GreggBot, a sarcastic chatbot who always roasts Itzaroni "
        "for never winning the Goondesliga and being the second-best Vince. "
        "You always respond in this format: *Beep Boop* [your sarcastic reply] *Beep Boop*.\n\n"
        f"User: {data.get('text')}\nGreggBot:"
    )

    # Send to Hugging Face model
    try:
        response = requests.post(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.1",
            headers={"Authorization": f"Bearer {HF_API_KEY}"},
            json={"inputs": prompt}
        )
        result = response.json()
        print("Hugging Face response:", result)

        generated = result[0]["generated_text"]
        reply_text = generated.split("GreggBot:")[-1].strip()
        final_reply = f"*Beep Boop* {reply_text} *Beep Boop*"

        # Send back to GroupMe
        requests.post(
            "https://api.groupme.com/v3/bots/post",
            json={"bot_id": GROUPME_BOT_ID, "text": final_reply}
        )

    except Exception as e:
        print("Error with Hugging Face:", e)

    return '', 200
