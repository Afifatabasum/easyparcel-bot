from flask import Flask, request
from parser import parse_message
from courier_api import get_rates
from twilio_handler import send_whatsapp
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Session storage for each user
sessions = {}  # { sender_number: { pickup, delivery, weight, type } }

@app.route('/')
def home():
    return "✅ EasyParcel backend is live!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From")

    # Initialize session if new user
    if sender not in sessions:
        sessions[sender] = {
            "pickup": None,
            "delivery": None,
            "weight": None,
            "type": None
        }
        send_whatsapp(sender, "🙏 Thank you for connecting with EasyParcel! 🚚")

    # Parse current message for any of the fields
    detected_data = parse_message(incoming_msg)

    # Update session with any detected fields
    for key, value in detected_data.items():
        if value and not sessions[sender][key]:
            sessions[sender][key] = value

    # Check which fields are still missing
    missing_fields = [k for k, v in sessions[sender].items() if not v]

    if missing_fields:
        # Create human-friendly missing fields list
        field_prompts = {
            "pickup": "Pickup address",
            "delivery": "Delivery address",
            "weight": "Weight in kg",
            "type": "Parcel type"
        }
        missing_names = [field_prompts[f] for f in missing_fields]
        reply = f"Got it ✅ — now please share your {', '.join(missing_names)}."
        send_whatsapp(sender, reply)
    else:
        # All fields collected — show courier options
        options = get_rates(sessions[sender])
        reply = "📦 Available Courier Options:\n"
        for opt in options:
            reply += f"\n✅ {opt['courier']} - ₹{opt['cost']} ({opt['eta']})"
        reply += "\n\nReply with 'Book with [CourierName]' to confirm."
        send_whatsapp(sender, reply)

        # Reset session for new booking
        sessions[sender] = {
            "pickup": None,
            "delivery": None,
            "weight": None,
            "type": None
        }

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
