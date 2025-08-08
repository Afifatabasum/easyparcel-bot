from flask import Flask, request
from parser import parse_message
from courier_api import get_rates
from twilio_handler import send_whatsapp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def home():
    return "✅ EasyParcel backend is live!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.form.get("Body")
    sender = request.form.get("From")

      

    parsed = parse_message(incoming_msg)

    if not parsed:
        reply = "❌ Sorry, I couldn't understand. Please send:\nPickup:\nDelivery:\nWeight:\nType:"
        send_whatsapp(sender, reply)
        return "OK", 200

    options = get_rates(parsed)
    reply = "📦 Available Courier Options:\n"
    for opt in options:
        reply += f"\n✅ {opt['courier']} - ₹{opt['cost']} ({opt['eta']})"
    reply += "\n\nReply with 'Book with [CourierName]' to confirm."

    send_whatsapp(sender, reply)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Use Render's port if available
    app.run(host="0.0.0.0", port=port)

