from flask import Flask, request
from parser import parse_message
from courier_api import get_rates, serviceable_cities
from twilio_handler import send_whatsapp
import os
from dotenv import load_dotenv
import re
from rapidfuzz import process, fuzz

load_dotenv()
app = Flask(__name__)

# Store user conversation data
user_data = {}
last_customer_details = {}  # For "same as last time" feature

@app.route('/')
def home():
    return "✅ EasyParcel backend is live!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From")

    # Handle booking cancellation
    if incoming_msg.lower() == "cancel booking":
        user_data.pop(sender, None)
        send_whatsapp(sender, "❌ Booking cancelled. You can start again anytime.")
        return "OK", 200

    # "Same as last time" for returning customers
    if incoming_msg.lower() == "same as last time" and sender in last_customer_details:
        user_data[sender] = last_customer_details[sender].copy()
        send_whatsapp(sender, "📋 Using your last booking details.")
        return send_courier_options(sender)

    # If user is new
    if sender not in user_data:
        user_data[sender] = {}
        welcome_msg = (
            "Thank you for connecting with EasyParcel! 🚚\n\n"
            "To get courier options, please send:\n"
            "Pickup: <location>\n"
            "Delivery: <location>\n"
            "Weight: <e.g., 2 kg>\n"
            "Parcel Type: (optional)"
        )
        send_whatsapp(sender, welcome_msg)
        return "OK", 200

    # Parse booking confirmation
    book_match = re.search(r"book with\s+(.+)", incoming_msg.lower())
    if book_match and all(k in user_data[sender] for k in ["pickup", "delivery", "weight"]):
        courier_name = book_match.group(1).strip()
        details = user_data[sender]
        confirmation = (
            f"✅ Booking confirmed!\n\n"
            f"From: *{details.get('pickup')}*\n"
            f"To: *{details.get('delivery')}*\n"
            f"Weight: *{details.get('weight')} kg*\n"
            f"Courier: *{courier_name}*\n\n"
            f"📦 Thank you for choosing EasyParcel!"
        )
        send_whatsapp(sender, confirmation)
        last_customer_details[sender] = details.copy()
        user_data.pop(sender, None)
        return "OK", 200

    # Parse new message
    parsed = parse_message(incoming_msg) or {}
    for key, value in parsed.items():
        if key in ["pickup", "delivery"]:
            # Fuzzy city correction
            best_match, score, _ = process.extractOne(value, serviceable_cities, scorer=fuzz.token_sort_ratio)
            if score >= 80:
                user_data[sender][key] = best_match
            else:
                send_whatsapp(sender, f"⚠️ '{value}' not found. Did you mean '{best_match}'?")
                return "OK", 200
        else:
            user_data[sender][key] = value

    # Check missing fields
    required_fields = ["pickup", "delivery", "weight"]
    missing = [f for f in required_fields if f not in user_data[sender]]
    if missing:
        send_whatsapp(sender, "Got it 👍 Please provide:\n" + "\n".join(missing))
        return "OK", 200

    # Handle filters
    if "cheapest" in incoming_msg.lower():
        return send_courier_options(sender, sort_by="price")
    elif "fastest" in incoming_msg.lower():
        return send_courier_options(sender, sort_by="speed")

    # Send all courier options
    return send_courier_options(sender)

def send_courier_options(sender, sort_by=None):
    details = user_data[sender]
    options = get_rates(details)

    if sort_by == "price":
        options = sorted(options, key=lambda x: x["cost"])
        options = [options[0]]  # only show cheapest
    elif sort_by == "speed":
        options = sorted(options, key=lambda x: int(x["eta"].split("-")[0]))
        options = [options[0]]  # only show fastest

    reply = "📦 Available Courier Options:\n"
    for opt in options:
        reply += f"\n✅ {opt['courier']} - ₹{opt['cost']} ({opt['eta']})"
    reply += "\n\nReply with 'Book with [CourierName]' to confirm."

    send_whatsapp(sender, reply)
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
