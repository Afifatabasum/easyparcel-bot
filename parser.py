import re

def parse_message(msg):
    try:
        data = {}

        # Normalize message: remove unwanted punctuation except colon/dot
        clean_msg = re.sub(r"[^\w\s:.]", " ", msg)
        clean_msg = re.sub(r"\s+", " ", clean_msg).strip()

        lines = clean_msg.split('\n')

        # 1. Try line-by-line parsing first
        for line in lines:
            lower = line.lower().strip()

            # Pickup detection by keyword
            if 'pickup' in lower or lower.startswith('from '):
                value = line.split(':')[-1].strip()
                if looks_like_location(value):
                    data['pickup'] = value

            # Delivery detection by keyword
            elif 'delivery' in lower or lower.startswith('to '):
                value = line.split(':')[-1].strip()
                if looks_like_location(value):
                    data['delivery'] = value

            # Weight detection
            elif 'weight' in lower:
                weight_str = line.split(':')[-1].strip().replace('kg', '').replace('kgs', '').strip()
                if re.match(r"^\d+(\.\d+)?$", weight_str):
                    data['weight'] = float(weight_str)

            # Parcel type detection
            elif 'type' in lower or 'parcel' in lower:
                value = line.split(':')[-1].strip()
                data['type'] = value

        # 2. Free text detection

        # a) If no pickup/delivery yet, check for "X to Y" pattern in the whole message
        if 'pickup' not in data or 'delivery' not in data:
            to_pattern = re.search(r"([a-zA-Z\s\.\-]+)\s+to\s+([a-zA-Z\s\.\-]+)", clean_msg, re.IGNORECASE)
            if to_pattern:
                pickup_candidate = to_pattern.group(1).strip()
                delivery_candidate = to_pattern.group(2).strip()

                if 'pickup' not in data and looks_like_location(pickup_candidate):
                    data['pickup'] = pickup_candidate

                if 'delivery' not in data and looks_like_location(delivery_candidate):
                    data['delivery'] = delivery_candidate

        # b) Keyword-based fallback pickup detection
        if 'pickup' not in data:
            m = re.search(r"(?:pickup|from)\s*[:\-]?\s*([a-zA-Z\s\.\-]+)", clean_msg, re.IGNORECASE)
            if m and looks_like_location(m.group(1).strip()):
                data['pickup'] = m.group(1).strip()

        # Keyword-based fallback delivery detection
        if 'delivery' not in data:
            m = re.search(r"(?:delivery|to)\s*[:\-]?\s*([a-zA-Z\s\.\-]+)", clean_msg, re.IGNORECASE)
            if m and looks_like_location(m.group(1).strip()):
                data['delivery'] = m.group(1).strip()

        # Weight fallback
        if 'weight' not in data:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(?:kg|kgs|kilogram|kilograms?)", clean_msg, re.IGNORECASE)
            if m:
                data['weight'] = float(m.group(1))

        # Parcel type fallback
        if 'type' not in data:
            m = re.search(r"(?:type|parcel|item)\s*[:\-]?\s*([a-zA-Z\s\.\-]+)", clean_msg, re.IGNORECASE)
            if m:
                data['type'] = m.group(1).strip()

        return data

    except:
        return {}

def looks_like_location(text):
    """
    Simple check if text looks like a city/town/place:
    - Only letters, spaces, dots, hyphens allowed
    - Length > 2 characters
    """
    if not text:
        return False
    if len(text) < 3:
        return False
    if re.fullmatch(r"[a-zA-Z\s\.\-]+", text):
        return True
    return False
