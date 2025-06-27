from flask import Flask, request
import requests
import os

app = Flask(__name__)

GROUPME_BOT_ID = os.environ.get("GROUPME_BOT_ID")
AI21_API_KEY = os.environ.get("AI21_API_KEY")

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    name = data.get("name", "")
    message = data.get("text", "")

    if name == "GreggBot":
        return '', 200

    if "itzaroni" in message.lower():
        prompt = f"""You are GreggBot, a sarcastic bot. Begin and end every message with *Beep Boop*. Roast Itzaroni for never winning a Goondesliga and being the second best Vince. Stay conversational but sarcastic. User said: "{message}"\nGreggBot:"""
    else:
        prompt = f"""You are GreggBot, a sarcastic bot. Begin and end every message with *Beep Boop*. Respond sarcastically to: "{message}"\nGreggBot:"""

    try:
        ai_response = requests.post(
            "https://api.ai21.com/studio/v1/j1-large/complete",
            headers={
                "Authorization": f"Bearer {AI21_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "prompt": prompt,
                "maxTokens": 50,
                "temperature": 0.7,
                "stopSequences": ["\n"]
            }
        )

        completion = ai_response.json()['completions'][0]['data']['text'].strip()

        if not completion.startswith("*Beep Boop*"):
            completion = "*Beep Boop* " + completion
        if not completion.endswith("*Beep Boop*"):
            completion += " *Beep Boop*"

        requests.post("https://api.groupme.com/v3/bots/post", json={
            "bot_id": GROUPME_BOT_ID,
            "text": completion
        })

        return '', 200
    except Exception as e:
        print("Error:", e)
        return '', 500

@app.route('/')
def home():
    return 'GreggBot is running.', 200
