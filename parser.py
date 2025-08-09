import re

def parse_message(msg):
    try:
        data = {}
        lines = msg.split('\n')

        # 1️⃣ Try exact line-by-line parsing first
        for line in lines:
            lower = line.lower()
            if 'pickup' in lower or lower.startswith('from'):
                data['pickup'] = line.split(':')[-1].strip()
            elif 'delivery' in lower or lower.startswith('to'):
                data['delivery'] = line.split(':')[-1].strip()
            elif 'weight' in lower:
                weight_str = re.search(r"(\d+(?:\.\d+)?)", line)
                if weight_str:
                    data['weight'] = float(weight_str.group(1))
            elif 'type' in lower or 'parcel' in lower:
                data['type'] = line.split(':')[-1].strip()

        # 2️⃣ If still missing fields, try free-text detection
        if 'pickup' not in data:
            pickup_match = re.search(r"(pickup|from)\s*[:\-]?\s*([a-zA-Z\s]+)", msg, re.IGNORECASE)
            if pickup_match:
                data['pickup'] = pickup_match.group(2).strip()

        if 'delivery' not in data:
            delivery_match = re.search(r"(delivery|to)\s*[:\-]?\s*([a-zA-Z\s]+)", msg, re.IGNORECASE)
            if delivery_match:
                data['delivery'] = delivery_match.group(2).strip()

        if 'weight' not in data:
            weight_match = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kilograms?)?", msg, re.IGNORECASE)
            if weight_match:
                data['weight'] = float(weight_match.group(1))

        if 'type' not in data:
            type_match = re.search(r"(type|parcel|item)\s*[:\-]?\s*([a-zA-Z\s]+)", msg, re.IGNORECASE)
            if type_match:
                data['type'] = type_match.group(2).strip()

        # Return only if we have enough info
        if all(k in data for k in ["pickup", "delivery", "weight", "type"]):
            return data
        return None

    except:
        return None
