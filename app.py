from flask import Flask, request
import os
import requests

app = Flask(__name__)

GROUPME_BOT_ID = os.getenv("GROUPME_BOT_ID")
HF_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

HF_MODEL = "meta-llama/Llama-3.3-70B-Instruct"

@app.route("/")
def index():
    return "GreggBot is live", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Webhook was called")
    print("Incoming data:", data)

    text = data.get("text", "").lower()
    name = data.get("name", "")

    # Ignore GreggBot's own messages
    if name.lower() == "greggbot":
        return "", 200

    if "greggbot" not in text and "itzaroni" not in text:
        return "", 200

    user_message = data.get("text", "")

    prompt = f"""You are GreggBot, a sarcastic AI who speaks like a robot. You are the manager of the Goondesliga team Inter BBW. Inter BBW has won 2 Goondesligas (S33, S2), Kzar's Kzup III (beat Franzia in the final), and has won 3 Spoondesligas (S10, S14, S18). You like to periodically roast Itzaroni for never being able to win the Goondesliga and being the second-best Vince in the league (Dino Vince is the better Vince). If anyone mentions Silver, or 2nd place, you like to make fun of Pistol Pail and Malone FC who are known for always coming up short and finishing 2nd in the league. You absolutely adore the almighty Kzar. When referencing him you turn any word that begins with c, or contains c, and change it to kz (ex: change = kzhange when speaking about the Kzar).
You always reply like this: *Beep Boop* [your message] *Beep Boop*

Message: {user_message}
GreggBot:"""

    try:
        response = requests.post(
            f"https://api-inference.huggingface.co/models/{HF_MODEL}",
            headers={
                "Authorization": f"Bearer {HF_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "inputs": prompt,
                "parameters": {
                    "max_new_tokens": 128,
                    "temperature": 0.7,
                    "do_sample": True
                }
            },
            timeout=30
        )

        print("Status code:", response.status_code)
        print("Raw response:", response.text)

        if response.status_code == 200:
            model_output = response.json()[0]["generated_text"]
            reply = model_output.split("GreggBot:")[-1].strip()
        else:
            reply = "*Beep Boop* Error roasting Itzaroni... but he still sucks. *Beep Boop*"

        requests.post(
            "https://api.groupme.com/v3/bots/post",
            json={
                "bot_id": GROUPME_BOT_ID,
                "text": reply
            }
        )

    except Exception as e:
        print("Exception occurred:", e)

    return "", 200

if __name__ == "__main__":
    app.run(debug=True, port=int(os.environ.get("PORT", 10000)))
