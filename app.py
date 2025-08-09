@app.route("/whatsapp", methods=["POST"])
def whatsapp_webhook():
    incoming_msg = request.form.get("Body", "").strip()
    sender = request.form.get("From")

    # Step 1: Try parsing the incoming message
    parsed = parse_message(incoming_msg)
    if not parsed:
        parsed = smart_parse(incoming_msg)

    # Step 2: If no valid details found → send welcome + instructions
    if not parsed or not all(k in parsed for k in ["pickup", "delivery", "weight", "type"]):
        welcome_msg = (
            "🙏 Thank you for connecting with EasyParcel!\n\n"
            "📦 To get courier options, please send the following details:\n"
            "Pickup: <Your pickup city>\n"
            "Delivery: <Your delivery city>\n"
            "Weight: <Weight in kg>\n"
            "Type: <Parcel type>\n\n"
            "Example:\nPickup: Chennai\nDelivery: Bangalore\nWeight: 2kg\nType: Documents"
        )
        send_whatsapp(sender, welcome_msg)
        return "OK", 200

    # Step 3: If details found → send courier options
    options = get_rates(parsed)
    reply = "📦 Available Courier Options:\n"
    for opt in options:
        reply += f"\n✅ {opt['courier']} - ₹{opt['cost']} ({opt['eta']})"
    reply += "\n\nReply with 'Book with [CourierName]' to confirm."
    send_whatsapp(sender, reply)

    return "OK", 200


def smart_parse(message):
    """Flexible parser to detect pickup, delivery, weight, and type from free text"""
    data = {}

    pickup_match = re.search(r"(pickup|from)\s*[:\-]?\s*([a-zA-Z\s]+)", message, re.IGNORECASE)
    if pickup_match:
        data["pickup"] = pickup_match.group(2).strip()

    delivery_match = re.search(r"(delivery|to)\s*[:\-]?\s*([a-zA-Z\s]+)", message, re.IGNORECASE)
    if delivery_match:
        data["delivery"] = delivery_match.group(2).strip()

    weight_match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilograms?)", message, re.IGNORECASE)
    if weight_match:
        data["weight"] = float(weight_match.group(1))  # ✅ store as float

    type_match = re.search(r"(type|parcel|item)\s*[:\-]?\s*([a-zA-Z\s]+)", message, re.IGNORECASE)
    if type_match:
        data["type"] = type_match.group(2).strip()

    return data if data else None
