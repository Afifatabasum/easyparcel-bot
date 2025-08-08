import os
from twilio.rest import Client
from dotenv import load_dotenv

load_dotenv()  # Only needed for local testing; safe to leave

TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio sandbox number

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def send_whatsapp(to, message):
    client.messages.create(
        body=message,
        from_=WHATSAPP_NUMBER,
        to=to
    )
