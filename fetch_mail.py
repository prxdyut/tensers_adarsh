import imaplib
import email
import time
import threading
import requests  # For sending data to another model/API
import base64
from flask import Flask, jsonify

# Gmail IMAP Configuration
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "sujaldyavanapelli80@gmail.com"
EMAIL_PASSWORD = "iigk svlo fehn clls"  # Use App Password, NOT your Gmail password

# Target Model API Endpoint
MODEL_API_URL = "http://your-model-endpoint.com/process"  # 🔹 Replace with actual URL

app = Flask(__name__)

latest_email_id = None  # Stores the latest fetched email ID
latest_emails = []  # Stores new emails


def extract_email_headers(msg):
    """Extract headers required for email spoofing and phishing detection."""
    headers = {
        "From": msg["From"],
        "To": msg["To"],
        "Date": msg["Date"],
        "Subject": msg["Subject"],
        "Message-ID": msg["Message-ID"],
        "Reply-To": msg["Reply-To"],
        "Return-Path": msg["Return-Path"],
        "Received-SPF": msg.get("Received-SPF", None),  # SPF authentication
        "DKIM-Signature": msg.get("DKIM-Signature", None),  # DKIM signature
        "Received": msg.get_all("Received"),  # Email hop tracking
    }
    return headers


def extract_email_body_and_attachments(msg):
    """Extracts email body (text only) and attachments."""
    body_text = ""
    attachments = []

    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if "attachment" in content_disposition:
                # Extract attachment content
                filename = part.get_filename()
                file_data = part.get_payload(decode=True)
                if file_data:
                    encoded_file = base64.b64encode(file_data).decode("utf-8")
                    attachments.append({"filename": filename, "content": encoded_file})
            elif content_type == "text/plain":
                # Extract only plain text body
                payload = part.get_payload(decode=True)
                if payload:
                    body_text = payload.decode(errors="ignore")
    else:
        body_text = msg.get_payload(decode=True).decode(errors="ignore")

    return {"text": body_text, "attachments": attachments}


def fetch_new_email():
    """Fetch only the latest new email that has just entered the inbox."""
    global latest_email_id, latest_emails
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        # Search for all emails (latest ones are at the end)
        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print("✅ No emails in inbox.")
            return

        latest_fetched_id = email_ids[-1]  # Get the latest email ID

        if latest_email_id == latest_fetched_id:
            print("✅ No new emails.")
            return  # No new emails, return

        # Fetch only the latest new email
        result, data = mail.fetch(latest_fetched_id, "(RFC822)")
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])

                email_data = {
                    "headers": extract_email_headers(msg),
                    "body": extract_email_body_and_attachments(msg),
                }

                latest_emails = [email_data]  # Store only the new email
                latest_email_id = latest_fetched_id  # Update last fetched email ID

                print("📩 New Email Fetched!", email_data["headers"]["Subject"])

                # Send the extracted email data to the external model/API
                send_to_model(email_data)

        mail.logout()
    except Exception as e:
        print("❌ Error fetching email:", str(e))


def send_to_model(email_data):
    """Sends the extracted email data to an external model/API."""
    try:
        response = requests.post(MODEL_API_URL, json=email_data, timeout=10)
        if response.status_code == 200:
            print("✅ Successfully sent email data to model.")
        else:
            print("❌ Model API returned an error:", response.text)
    except Exception as e:
        print("❌ Failed to send data to model:", str(e))


def check_for_new_emails():
    """Continuously check for new emails every 10 seconds."""
    while True:
        fetch_new_email()
        time.sleep(10)  # Poll every 10 seconds


# Start the email listener in a separate thread
threading.Thread(target=check_for_new_emails, daemon=True).start()


@app.route("/")
def index():
    return "📬 Gmail Email Spoofing & Phishing Detection API Running!"


@app.route("/latest-email", methods=["GET"])
def get_latest_email():
    """API endpoint to get the latest email with headers & full body."""
    return jsonify(latest_emails)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
