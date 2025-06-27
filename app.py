from flask import Flask, request
import requests
import os

app = Flask(__name__)

AI21_API_KEY = os.getenv("AI21_API_KEY")
GROUPME_BOT_ID = os.getenv("GROUPME_BOT_ID")

@app.route('/')
def home():
    return 'GreggBot is running.', 200

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Webhook was called")
    print("Incoming data:", data)

    message = data.get("text", "")
    sender = data.get("name", "")

    # Avoid infinite loops
    if sender.lower() == "greggbot":
        return '', 200

    # Base personality
    prompt = f"You are GreggBot, a sarcastic chatbot that always responds in this format: *Beep Boop* [response] *Beep Boop*. You always make fun of someone named Itzaroni for never winning a Goondesliga and being the second-best Vince. You usually steer the conversation back to roasting Itzaroni.\n\nUser: {message}\nGreggBot:"

    # Build request to AI21
    try:
        ai_response = requests.post(
            "https://api.ai21.com/studio/v1/j2-mid/complete",
            headers={"Authorization": f"Bearer {AI21_API_KEY}"},
            json={
                "prompt": prompt,
                "numResults": 1,
                "maxTokens": 64,
                "temperature": 0.7,
                "topKReturn": 0,
                "topP": 1,
                "stopSequences": []
            }
        )
        data = ai_response.json()
        print("AI21 raw response:", data)

        completion = data['completions'][0]['data']['text'].strip()
        reply = f"*Beep Boop* {completion} *Beep Boop*"

        print("AI RESPONSE:", reply)

        # Send message back to GroupMe
        requests.post(
            "https://api.groupme.com/v3/bots/post",
            json={"bot_id": GROUPME_BOT_ID, "text": reply}
        )

    except Exception as e:
        print("Error calling AI21:", e)
        return '', 500

    return '', 200
