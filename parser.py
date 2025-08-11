import re

def parse_message(msg):
    try:
        data = {}

        # Normalize: remove unwanted punctuation except colon/dot/hyphen
        clean_msg = re.sub(r"[^\w\s:.\-]", " ", msg)
        clean_msg = re.sub(r"\s+", " ", clean_msg).strip()

        lines = clean_msg.split('\n')

        # 1. Line-by-line parsing
        for line in lines:
            lower = line.lower().strip()

            # Pickup detection
            if 'pickup' in lower or lower.startswith('from '):
                value = line.split(':')[-1].strip()
                if looks_like_location(value):
                    data['pickup'] = value

            # Delivery detection
            elif 'delivery' in lower or lower.startswith('to '):
                value = line.split(':')[-1].strip()
                if looks_like_location(value):
                    data['delivery'] = value

            # Weight detection (kg or g)
            elif 'weight' in lower:
                weight_str = line.split(':')[-1].strip().lower()
                weight_match = re.match(r"(\d+(?:\.\d+)?)\s*(kg|kgs|g|grams?)", weight_str)
                if weight_match:
                    weight = float(weight_match.group(1))
                    unit = weight_match.group(2)
                    if unit.startswith('g'):
                        weight = weight / 1000  # convert g to kg
                    data['weight'] = weight

            # Parcel type detection
            elif 'type' in lower or 'parcel' in lower:
                value = line.split(':')[-1].strip()
                data['type'] = value

        # 2. Free text detection
        # a) "X to Y" pattern
        if 'pickup' not in data or 'delivery' not in data:
            to_pattern = re.search(r"([a-zA-Z\s.\-]+)\s+to\s+([a-zA-Z\s.\-]+)", clean_msg, re.IGNORECASE)
            if to_pattern:
                pickup_candidate = to_pattern.group(1).strip()
                delivery_candidate = to_pattern.group(2).strip()
                if 'pickup' not in data and looks_like_location(pickup_candidate):
                    data['pickup'] = pickup_candidate
                if 'delivery' not in data and looks_like_location(delivery_candidate):
                    data['delivery'] = delivery_candidate

        # b) Fallback pickup
        if 'pickup' not in data:
            m = re.search(r"(?:pickup|from)\s*[:\-]?\s*([a-zA-Z\s.\-]+)", clean_msg, re.IGNORECASE)
            if m and looks_like_location(m.group(1).strip()):
                data['pickup'] = m.group(1).strip()

        # c) Fallback delivery
        if 'delivery' not in data:
            m = re.search(r"(?:delivery|to)\s*[:\-]?\s*([a-zA-Z\s.\-]+)", clean_msg, re.IGNORECASE)
            if m and looks_like_location(m.group(1).strip()):
                data['delivery'] = m.group(1).strip()

        # d) Fallback weight
        if 'weight' not in data:
            m = re.search(r"(\d+(?:\.\d+)?)\s*(kg|kgs|g|grams?)", clean_msg, re.IGNORECASE)
            if m:
                weight = float(m.group(1))
                unit = m.group(2)
                if unit.startswith(('g', 'G')):
                    weight = weight / 1000
                data['weight'] = weight

        # e) Fallback parcel type
        if 'type' not in data:
            m = re.search(r"(?:type|parcel|item)\s*[:\-]?\s*([a-zA-Z\s.\-]+)", clean_msg, re.IGNORECASE)
            if m:
                data['type'] = m.group(1).strip()

        return data

    except Exception as e:
        print("Parser error:", e)
        return {}


def looks_like_location(text):
    """Check if text looks like a valid location"""
    if not text:
        return False
    if len(text) < 3:
        return False
    # Simple heuristic: location should contain letters (not just numbers or symbols)
    if not re.search(r"[a-zA-Z]", text):
        return False
    return True

