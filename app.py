from flask import Flask, request
from parser import parse_message
from courier_api import get_rates
from twilio_handler import send_whatsapp
import os
from dotenv import load_dotenv
import re

load_dotenv()
app = Flask(__name__)

# Store user conversation data
user_data = {}

@app.route('/')
def home():
    return "✅ EasyParcel backend is live!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From")

    # If first message from user, initialize session
    if sender not in user_data:
        user_data[sender] = {}
        welcome_msg = (
            "Thank you for connecting with EasyParcel!\n\n"
            "📦 To get courier options, please send the following details:\n"
            "Pickup:\n"
            "Delivery:\n"
            "Weight:\n"
            "Parcel Type: (optional)"
        )
        send_whatsapp(sender, welcome_msg)
        return "OK", 200

    # Check if user is booking
    book_match = re.search(r"book with\s+(.+)", incoming_msg, re.IGNORECASE)
    if book_match and "pickup" in user_data[sender] and "delivery" in user_data[sender] and "weight" in user_data[sender]:
        courier_name = book_match.group(1).strip()
        details = user_data[sender]
        confirmation = (
            f"✅ Booking confirmed!\n\n"
            f"You are sending a parcel from *{details['pickup']}* to *{details['delivery']}* "
            f"weighing *{details['weight']} kg* via *{courier_name}*.\n\n"
            f"📦 Thank you for choosing EasyParcel!"
        )
        send_whatsapp(sender, confirmation)
        user_data.pop(sender, None)  # clear session after booking
        return "OK", 200

    # Parse current message
    parsed = parse_message(incoming_msg)
    for key, value in parsed.items():
        user_data[sender][key] = value

    # Determine missing required fields (parcel type optional)
    required_fields = ["pickup", "delivery", "weight"]
    missing = [f for f in required_fields if f not in user_data[sender]]

    if missing:
        ask_msg = "Got it. Please send the following details:\n" + "\n".join(missing)
        send_whatsapp(sender, ask_msg)
        return "OK", 200

    # All required details present → get courier rates
    details = user_data[sender]
    options = get_rates(details)
    reply = "📦 Available Courier Options:\n"
    for opt in options:
        reply += f"\n✅ {opt['courier']} - ₹{opt['cost']} ({opt['eta']})"
    reply += "\n\nReply with 'Book with [CourierName]' to confirm."

    send_whatsapp(sender, reply)
    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
