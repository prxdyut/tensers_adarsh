import imaplib
import email
import time
import threading
import base64
from flask import Flask, jsonify
from report_gen import run_phishing_detector

# Gmail IMAP Configuration
IMAP_SERVER = "imap.gmail.com"
IMAP_PORT = 993
EMAIL_ACCOUNT = "sujaldyavanapelli80@gmail.com"
EMAIL_PASSWORD = "iigk svlo fehn clls"  # Use App Password, NOT your Gmail password

app = Flask(__name__)

latest_email_id = None  # Stores the latest fetched email ID
latest_email_data = {}  # Stores the latest email data with phishing analysis

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
        "Received-SPF": msg.get("Received-SPF", None),
        "DKIM-Signature": msg.get("DKIM-Signature", None),
        "Received": msg.get_all("Received"),
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
                filename = part.get_filename()
                file_data = part.get_payload(decode=True)
                if file_data:
                    encoded_file = base64.b64encode(file_data).decode("utf-8")
                    attachments.append({"filename": filename, "content": encoded_file})
            elif content_type == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body_text = payload.decode(errors="ignore")
    else:
        body_text = msg.get_payload(decode=True).decode(errors="ignore")

    return {"text": body_text, "attachments": attachments}

def fetch_new_email():
    """Fetch only the latest new email that has just entered the inbox."""
    global latest_email_id, latest_email_data
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        result, data = mail.search(None, "ALL")
        email_ids = data[0].split()

        if not email_ids:
            print("✅ No emails in inbox.")
            return

        latest_fetched_id = email_ids[-1]

        if latest_email_id == latest_fetched_id:
            print("✅ No new emails.")
            return

        result, data = mail.fetch(latest_fetched_id, "(RFC822)")
        for response_part in data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                
                email_headers = extract_email_headers(msg)
                email_body = extract_email_body_and_attachments(msg)["text"]
                
                print("📩 New Email Fetched!", email_headers["Subject"])
                
                # Send the extracted email data to the phishing detector function
                report, verdict, confidence, enhanced_report = run_phishing_detector(email_headers, email_body)
                
                latest_email_data = {
                    "headers": email_headers,
                    "body": email_body,
                    "report": report,
                    "verdict": verdict,
                    "confidence": confidence,
                    "enhanced_report": enhanced_report,
                }
                
                latest_email_id = latest_fetched_id
        
        mail.logout()
        
    except Exception as e:
        print("❌ Error fetching email:", str(e))

def check_for_new_emails():
    """Continuously check for new emails every 10 seconds."""
    while True:
        fetch_new_email()
        time.sleep(10)

# Start the email listener in a separate thread
threading.Thread(target=check_for_new_emails, daemon=True).start()

@app.route("/")
def index():
    return "📬 Gmail Email Spoofing & Phishing Detection API Running!"

@app.route("/latest-email", methods=["GET"])
def get_latest_email():
    """API endpoint to get the latest email with phishing detection results."""
    return jsonify(latest_email_data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
