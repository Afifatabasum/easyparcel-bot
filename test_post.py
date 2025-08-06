import requests

# URL where your Flask app is running
url = "http://localhost:5000/whatsapp"

# Simulated WhatsApp message content
data = {
    "Body": "Pickup: 28 MG Road, Bengaluru\nDrop: 1224 Anna Nagar, Chennai\nWeight: 3kg",
    "From": "whatsapp:+919999999999"  # Just a test sender number
}

# Send the POST request
response = requests.post(url, data=data)

# Print the response from your Flask app
print("Response from Flask app:")
print(response.text)
