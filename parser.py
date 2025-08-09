import re

def parse_message(msg):
    """Detect pickup, delivery, weight, and type in any order from free text."""
    data = {
        "pickup": None,
        "delivery": None,
        "weight": None,
        "type": None
    }

    # Normalize message (remove extra spaces & punctuation)
    msg_clean = re.sub(r"[^\w\s\.]", " ", msg)
    msg_clean = re.sub(r"\s+", " ", msg_clean).strip()

    # Pickup city/address
    pickup_match = re.search(r"(pickup|from)\s*[:\-]?\s*([a-zA-Z\s]+)", msg_clean, re.IGNORECASE)
    if pickup_match:
        data["pickup"] = pickup_match.group(2).strip()

    # Delivery city/address
    delivery_match = re.search(r"(delivery|to)\s*[:\-]?\s*([a-zA-Z\s]+)", msg_clean, re.IGNORECASE)
    if delivery_match:
        data["delivery"] = delivery_match.group(2).strip()

    # Weight (integer or float)
    weight_match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilograms?)?", msg_clean, re.IGNORECASE)
    if weight_match:
        try:
            data["weight"] = float(weight_match.group(1))
        except:
            pass

    # Type of parcel
    type_match = re.search(r"(type|parcel|item)\s*[:\-]?\s*([a-zA-Z\s]+)", msg_clean, re.IGNORECASE)
    if type_match:
        data["type"] = type_match.group(2).strip()

    return {k: v for k, v in data.items() if v}
