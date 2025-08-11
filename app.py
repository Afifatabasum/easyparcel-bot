from flask import Flask, request
from courier_api import get_rates, serviceable_cities
from twilio_handler import send_whatsapp
import os
from dotenv import load_dotenv
import re
from rapidfuzz import process, fuzz
import string
import requests

load_dotenv()
app = Flask(__name__)

# Store user conversation data
user_data = {}
last_customer_details = {}  # For "same as last time" feature

GOOGLE_MAPS_KEY = os.getenv("GOOGLE_MAPS_KEY")  # Optional, if you want exact lat/lng

def robust_parse(message):
    """
    Extracts pickup, delivery, weight, and parcel type from a WhatsApp message.
    Works regardless of case, punctuation, or messy formatting.
    """
    msg = message.lower().strip()

    # Keep commas, slashes, and hyphens for addresses
    allowed_punct = ",-/"
    msg_cleaned = "".join(ch for ch in msg if ch.isalnum() or ch in allowed_punct or ch.isspace())

    data = {}

    # Pickup address
    pickup_match = re.search(r"pickup\s+(.+?)(?=\s+delivery|\s+weight|\s+parcel|$)", msg_cleaned)
    if pickup_match:
        data["pickup"] = pickup_match.group(1).strip().title()

    # Delivery address
    delivery_match = re.search(r"delivery\s+(.+?)(?=\s+weight|\s+parcel|$)", msg_cleaned)
    if delivery_match:
        data["delivery"] = delivery_match.group(1).strip().title()

    # Weight (numbers + optional "kg")
    weight_match = re.search(r"weight\s+([\d\.]+)", msg_cleaned)
    if weight_match:
        try:
            data["weight"] = float(weight_match.group(1))
        except ValueError:
            pass

    # Parcel type
    parcel_match = re.search(r"parcel\s*type\s+(.+)", msg_cleaned)
    if parcel_match:
        data["parcel_type"] = parcel_match.group(1).strip().title()

    return data

def get_lat_lng(address):
    """
    Optional: Uses Google Maps API to get lat/lng for a given address.
    """
    if not GOOGLE_MAPS_KEY:
        return None, None
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_KEY}"
    res = requests.get(url).json()
    if res['status'] == 'OK':
        location = res['results'][0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None

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
        send_whatsapp(sender, "❌ Booking cancelled. You can start your booking again anytime.")
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
            "Pickup: <full address>\n"
            "Delivery: <full address>\n"
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
