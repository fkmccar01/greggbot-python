from flask import Flask, request
import os
import requests
from huggingface_hub import InferenceClient

app = Flask(__name__)

# Get env variables from Render
GROUPME_BOT_ID = os.getenv("GROUPME_BOT_ID")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")
MODEL_ID = "meta-llama/Llama-3.3-70B-Instruct"

# Set up Hugging Face Inference Client with Fireworks.ai as provider
client = InferenceClient(provider="fireworks-ai", api_key=HF_API_KEY)

@app.route("/")
def index():
    return "GreggBot is alive.", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Webhook was called")
    print("Incoming data:", data)

    text = data.get("text", "").lower()
    name = data.get("name", "")

    # Ignore messages from the bot itself
    if name.lower() == "greggbot":
        return "", 200

    # Only respond to messages that mention GreggBot or Itzaroni
    if "greggbot" not in text and "itzaroni" not in text:
        return "", 200

    # Craft sarcastic prompt
    prompt = [
        {
            "role": "user",
            "content": (
                "You are GreggBot, a sarcastic chatbot who always roasts Itzaroni "
                "for never winning the Goondesliga and being the second-best Vince. "
                "You always reply like this: *Beep Boop* [your reply] *Beep Boop*.\n\n"
                f"User: {data.get('text')}\nGreggBot:"
            ),
        }
    ]

    try:
        # Request completion from Llama 3.3 via Fireworks
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=prompt,
            max_tokens=128
        )

        reply_text = response.choices[0].message.content.strip()
        print("Hugging Face raw reply:", reply_text)

        # Send to GroupMe
        requests.post(
            "https://api.groupme.com/v3/bots/post",
            json={
                "bot_id": GROUPME_BOT_ID,
                "text": reply_text
            }
        )

    except Exception as e:
        print("Error talking to Hugging Face:", e)

    return "", 200

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 10000)))
