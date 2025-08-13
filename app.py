from flask import Flask, request
from parser import robust_parse
from courier_api import get_rates
from twilio_handler import send_whatsapp
import os
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

load_dotenv()

app = Flask(__name__)

# Store session data temporarily (in production use DB/Redis)
user_sessions = {}

# Initialize geocoder
geolocator = Nominatim(user_agent="easyparcel_bot")

def get_lat_lng_from_address(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        return None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None


@app.route("/")
def home():
    return "EasyParcel backend is live!"


@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    from_number = request.form.get("From", "")
    incoming_msg = request.form.get("Body", "").strip()

    # Normalize phone as session key
    session_id = from_number

    # Load or initialize session
    if session_id not in user_sessions:
        user_sessions[session_id] = {
            "pickup": None,
            "delivery": None,
            "weight": None,
            "parcel_type": None
        }

    session_data = user_sessions[session_id]

    # Parse message
    parsed = robust_parse(incoming_msg)

    # Update session with any newly found data
    for key in ["pickup", "delivery", "weight", "parcel_type"]:
        if parsed.get(key):
            session_data[key] = parsed[key]

    # Check missing required fields
    missing = []
    for field in ["pickup", "delivery", "weight"]:
        if not session_data[field]:
            missing.append(field)

    if missing:
        send_whatsapp(
            from_number,
            f"Please provide: {', '.join(missing)}"
        )
        return "OK", 200

    # Convert pickup & delivery to lat/lng
    pickup_lat, pickup_lng = get_lat_lng_from_address(session_data["pickup"])
    delivery_lat, delivery_lng = get_lat_lng_from_address(session_data["delivery"])

    # Store them in session
    session_data["pickup_lat"] = pickup_lat
    session_data["pickup_lng"] = pickup_lng
    session_data["delivery_lat"] = delivery_lat
    session_data["delivery_lng"] = delivery_lng

    # Get courier rates
    rates = get_rates(
        session_data["pickup"], session_data["delivery"], session_data["weight"]
    )

    # Confirmation message
    confirmation_msg = (
        f"✅ Details received:\n"
        f"Pickup: {session_data['pickup']} ({pickup_lat}, {pickup_lng})\n"
        f"Delivery: {session_data['delivery']} ({delivery_lat}, {delivery_lng})\n"
        f"Weight: {session_data['weight']} kg\n"
        f"Parcel type: {session_data.get('parcel_type', 'Not specified')}\n\n"
        f"📦 Available courier rates:\n{rates}"
    )

    send_whatsapp(from_number, confirmation_msg)

    # Reset session after sending confirmation
    user_sessions.pop(session_id, None)

    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
