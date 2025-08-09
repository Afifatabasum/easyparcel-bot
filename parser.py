import re

def parse_message(msg):
    try:
        data = {}

        # Clean message: remove punctuation except : and .
        clean_msg = re.sub(r"[^\w\s:.]", " ", msg)
        clean_msg = re.sub(r"\s+", " ", clean_msg).strip()

        lines = clean_msg.split('\n')

        # Line-by-line parsing
        for line in lines:
            lower = line.lower().strip()

            # Pickup detection
            if 'pickup' in lower or lower.startswith('from'):
                data['pickup'] = line.split(':')[-1].strip()

            # Delivery detection
            elif 'delivery' in lower or lower.startswith('to'):
                data['delivery'] = line.split(':')[-1].strip()

            # Weight detection
            elif 'weight' in lower:
                weight_str = line.split(':')[-1].strip().replace('kg', '').replace('kgs', '').strip()
                if weight_str.isdigit() or re.match(r"^\d+(\.\d+)?$", weight_str):
                    data['weight'] = float(weight_str)

            # Parcel type detection
            elif 'type' in lower or 'parcel' in lower:
                data['type'] = line.split(':')[-1].strip()

        # Free-text pickup
        if 'pickup' not in data:
            pickup_match = re.search(r"(pickup|from)\s*[:\-]?\s*(.+)", clean_msg, re.IGNORECASE)
            if pickup_match:
                data['pickup'] = pickup_match.group(2).strip()

        # Free-text delivery
        if 'delivery' not in data:
            delivery_match = re.search(r"(delivery|to)\s*[:\-]?\s*(.+)", clean_msg, re.IGNORECASE)
            if delivery_match:
                data['delivery'] = delivery_match.group(2).strip()

        # Free-text weight
        if 'weight' not in data:
            weight_match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kgs|kilogram|kilograms?)", clean_msg, re.IGNORECASE)
            if weight_match:
                data['weight'] = float(weight_match.group(1))

        # Free-text type
        if 'type' not in data:
            type_match = re.search(r"(type|parcel|item)\s*[:\-]?\s*(.+)", clean_msg, re.IGNORECASE)
            if type_match:
                data['type'] = type_match.group(2).strip()

        # Only require pickup, delivery, weight
        return data

    except:
        return {}
