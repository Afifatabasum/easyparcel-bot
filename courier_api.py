# courier_api.py
import os
from dotenv import load_dotenv

load_dotenv()

# Example list of cities your courier partners serve
# You can expand this list as needed
serviceable_cities = [
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Chennai",
    "Kolkata",
    "Pune",
    "Hyderabad",
    "Delhi",
    "Ahmedabad",
    "Jaipur",
    "Lucknow",
    "Surat",
    "Indore",
    "Nagpur"
]

def get_rates(data):
    """
    Mock courier rate API.
    In real use, call Shiprocket, Delhivery, or other courier APIs here.
    """
    pickup = data.get("pickup")
    delivery = data.get("delivery")
    weight = data.get("weight")

    # For now, return static mock rates
    return [
        {"courier": "Delhivery", "cost": 120, "eta": "2-3 days"},
        {"courier": "XpressBees", "cost": 100, "eta": "3-4 days"},
        {"courier": "BlueDart", "cost": 150, "eta": "1-2 days"}
    ]

def track_shipment(courier_name, tracking_id):
    """
    Mock shipment tracking.
    Replace with actual API integration for live tracking.
    """
    # In real use: call courier tracking API
    return {
        "courier": courier_name,
        "tracking_id": tracking_id,
        "status": "In Transit",
        "last_update": "2025-08-10 14:32",
        "estimated_delivery": "2025-08-13"
    }
