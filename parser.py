def parse_message(msg):
    try:
        data = {}
        lines = msg.split('\n')
        for line in lines:
            lower = line.lower()
            if 'pickup' in lower:
                data['pickup'] = line.split(':')[1].strip()
            elif 'delivery' in lower:
                data['delivery'] = line.split(':')[1].strip()
            elif 'weight' in lower:
                data['weight'] = float(line.split(':')[1].strip().replace('kg', '').strip())
            elif 'type' in lower:
                data['type'] = line.split(':')[1].strip()
        if 'pickup' in data and 'delivery' in data and 'weight' in data:
            return data
        return None
    except:
        return None
