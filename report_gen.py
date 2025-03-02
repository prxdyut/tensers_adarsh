import re
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle
from groq import Groq

# ----------------------------
# 1. Load the Trained Model and Tokenizer
# ----------------------------
def load_model_and_tokenizer(model_path, tokenizer_path):
    """
    Load the trained model and tokenizer.
    """
    # Load the model
    model = load_model(model_path)
    
    # Load the tokenizer
    with open(tokenizer_path, 'rb') as f:
        tokenizer = pickle.load(f)
    
    return model, tokenizer

# ----------------------------
# 2. Preprocess Text for LSTM Model
# ----------------------------
def preprocess_text(text, tokenizer, max_length=100):
    """
    Preprocess a single text input for prediction.
    """
    # Convert to sequence
    sequence = tokenizer.texts_to_sequences([text])
    
    # Pad the sequence
    padded_sequence = pad_sequences(sequence, maxlen=max_length, padding='post', truncating='post')
    
    return padded_sequence

# ----------------------------
# 3. Predict Phishing with LSTM Model
# ----------------------------
def predict_phishing(text, model, tokenizer, max_length=100):
    """
    Predict if an email is a phishing attempt.
    """
    # Preprocess the text
    processed_text = preprocess_text(text, tokenizer, max_length)
    
    # Make prediction
    prediction = model.predict(processed_text, verbose=0)[0][0]
    
    # Return prediction and confidence
    is_phishing = bool(prediction >= 0.5)
    confidence = prediction if is_phishing else 1 - prediction
    
    return is_phishing, confidence

# ----------------------------
# 4. Extract Header Status and Validate From/Reply-To
# ----------------------------
def extract_header_status(email_headers):
    """
    Extract SPF, DKIM, DMARC statuses, and validate From/Reply-To fields.
    """
    # Regex patterns to extract statuses
    spf_pattern = r"spf=(\w+)"
    dkim_pattern = r"dkim=(\w+)"
    dmarc_pattern = r"dmarc=(\w+)"
    from_pattern = r"From:\s*([^\s]+)"
    reply_to_pattern = r"Reply-To:\s*([^\s]+)"

    # Extract statuses
    spf_status = re.search(spf_pattern, email_headers, re.IGNORECASE)
    dkim_status = re.search(dkim_pattern, email_headers, re.IGNORECASE)
    dmarc_status = re.search(dmarc_pattern, email_headers, re.IGNORECASE)
    from_address = re.search(from_pattern, email_headers, re.IGNORECASE)
    reply_to_address = re.search(reply_to_pattern, email_headers, re.IGNORECASE)

    # Validate From and Reply-To fields
    if from_address and reply_to_address:
        from_address = from_address.group(1).lower()
        reply_to_address = reply_to_address.group(1).lower()
        from_reply_to_match = from_address == reply_to_address
    else:
        from_reply_to_match = False  # If either field is missing, consider it a mismatch

    # Return statuses and From/Reply-To validation
    return {
        "spf": spf_status.group(1).lower() if spf_status else "fail",
        "dkim": dkim_status.group(1).lower() if dkim_status else "fail",
        "dmarc": dmarc_status.group(1).lower() if dmarc_status else "fail",
        "from_reply_to_match": from_reply_to_match,
    }

# ----------------------------
# 5. Classify Email Based on Headers
# ----------------------------
def classify_email_from_headers(header_status):
    """
    Classify email as spam or not spam based on SPF, DKIM, DMARC, and From/Reply-To.
    """
    # Check if From and Reply-To match
    if not header_status["from_reply_to_match"]:
        return "Phishing", 0.95  # High confidence if From/Reply-To mismatch

    # Check SPF, DKIM, DMARC
    if (
        header_status["spf"] == "pass"
        and header_status["dkim"] == "pass"
        and header_status["dmarc"] == "pass"
    ):
        return "Not Phishing", 0.9  # High confidence when all checks pass
    else:
        # Calculate confidence based on how many checks failed
        failed_checks = sum(1 for status in ["spf", "dkim", "dmarc"] if header_status[status] != "pass")
        confidence = 0.5 + (0.15 * failed_checks)  # Base confidence + additional for each failed check
        return "Phishing", min(confidence, 0.95)  # Cap at 95% confidence

# ----------------------------
# 6. Extract Metadata from Email Content
# ----------------------------
def extract_metadata(email_content):
    """
    Extract metadata from email content:
    - Email length (number of words)
    - Presence of hyperlinks
    - Urgency indicators
    - Suspicious requests
    """
    # Email length (number of words)
    email_length = len(email_content.split())

    # Presence of hyperlinks
    hyperlink_pattern = r"https?://[^\s]+"
    has_hyperlinks = 1 if re.search(hyperlink_pattern, email_content) else 0

    # Urgency indicators
    urgency_keywords = ["urgent", "immediate", "action required", "important", 
                        "alert", "attention", "critical", "password", "account",
                        "suspended", "verify", "expires", "login", "security",
                        "update now", "limited time", "act now"]
    has_urgency = 1 if any(keyword in email_content.lower() for keyword in urgency_keywords) else 0

    # Check for suspicious requests
    suspicious_requests = ["bank details", "credit card", "verify account", 
                          "confirm identity", "update payment", "click here",
                          "follow link", "password reset"]
    has_suspicious_requests = 1 if any(req in email_content.lower() for req in suspicious_requests) else 0

    return {
        "email_length": email_length,
        "has_hyperlinks": has_hyperlinks,
        "has_urgency": has_urgency,
        "has_suspicious_requests": has_suspicious_requests
    }

# ----------------------------
# 7. Generate Report
# ----------------------------
def generate_report(email_headers, email_content, model, tokenizer):
    """
    Generate a comprehensive analysis report for an email.
    """
    # 1. Extract header status
    if email_headers:
        header_status = extract_header_status(email_headers)
        header_classification, header_confidence = classify_email_from_headers(header_status)
    else:
        header_status = {"spf": "unknown", "dkim": "unknown", "dmarc": "unknown", "from_reply_to_match": False}
        header_classification, header_confidence = "No headers provided", 0.0
    
    # 2. Extract metadata
    metadata = extract_metadata(email_content)
    
    # 3. LSTM model prediction
    is_phishing, model_confidence = predict_phishing(email_content, model, tokenizer)
    model_classification = "Not Phishing" if is_phishing else "Phishing"
    
    # 4. Combine signals for final verdict
    # Simple weighted average of header and model predictions
    if header_classification != "No headers provided":
        # Weight model prediction higher than headers
        final_score = (model_confidence * 0.7) + (header_confidence * 0.3)
        if model_classification == header_classification:
            final_verdict = model_classification
            confidence_level = max(model_confidence, header_confidence)
        else:
            # If they disagree, go with the higher confidence one
            final_verdict = model_classification if model_confidence > header_confidence else header_classification
            confidence_level = max(model_confidence, header_confidence) * 0.8  # Reduce confidence when signals disagree
    else:
        # If no headers, rely solely on model
        final_verdict = model_classification
        confidence_level = model_confidence
    
    # Adjust verdict based on metadata
    suspicious_score = metadata["has_hyperlinks"] + metadata["has_urgency"] + metadata.get("has_suspicious_requests", 0)
    if suspicious_score >= 2 and final_verdict == "Not Phishing":
        final_verdict = "Suspicious (Potential Phishing)"
        confidence_level *= 0.7  # Reduce confidence
    
    # Format the report
    report = f"""
    =========== EMAIL PHISHING ANALYSIS REPORT ===========
    
    FINAL VERDICT: {final_verdict.upper()} (Confidence: {confidence_level:.2%})
    
    1. HEADER ANALYSIS:
       - SPF: {header_status["spf"]}
       - DKIM: {header_status["dkim"]}
       - DMARC: {header_status["dmarc"]}
       - From/Reply-To Match: {"Yes" if header_status["from_reply_to_match"] else "No"}
       - Classification based on headers: {header_classification} (Confidence: {header_confidence:.2%})
    
    2. CONTENT ANALYSIS:
       - LSTM Model Prediction: {model_classification} (Confidence: {model_confidence:.2%})
       - Email Length: {metadata["email_length"]} words
       - Contains Hyperlinks: {"Yes" if metadata["has_hyperlinks"] else "No"}
       - Contains Urgency Indicators: {"Yes" if metadata["has_urgency"] else "No"}
       - Contains Suspicious Requests: {"Yes" if metadata.get("has_suspicious_requests", 0) else "No"}
    """
    
    report += "\n\n    =================================================="
    
    return report, final_verdict, confidence_level

# ----------------------------
# 8. Enhance Report with Groq API
# ----------------------------
def enhance_report_with_groq(report, verdict, confidence):
    """
    Use Groq API to generate a more comprehensive analysis of the report.
    """
    # Initialize Groq client
    client = Groq(api_key='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')

    # Construct the prompt
    prompt = f"""
        You are a cybersecurity expert specializing in email phishing detection. 
        Analyze the following phishing detection report and generate a more comprehensive analysis:

        {report}
        
        Based on this information, please provide an enhanced report that:
        
        1. Elaborates on the technical significance of each header check (SPF, DKIM, DMARC)
        2. Explains the security implications when these checks fail
        3. Provides detailed recommendations based on the verdict ("{verdict}" with {confidence:.2%} confidence)
        4. Explains common phishing tactics detected in the content analysis
        5. Includes additional educational information to help users identify similar phishing attempts
        6. Suggests best practices for email security
        
        Please maintain a professional tone suitable for cybersecurity reporting while making 
        the content accessible to non-technical users.
        """

    # Create the completion request
    completion = client.chat.completions.create(
        model="deepseek-r1-distill-llama-70b",
        messages=[
            {"role": "system", "content": "You are a cybersecurity expert specializing in email phishing detection."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.6,
        max_completion_tokens=4096,
        top_p=0.95,
        stream=True,
        stop=None,
    )

    # Stream the response
    enhanced_report = ""
    for chunk in completion:
        enhanced_report += chunk.choices[0].delta.content or ""
    
    return enhanced_report

# ----------------------------
# 9. Run Phishing Detector
# ----------------------------
def run_phishing_detector(email_headers, email_content):
    """
    Run the phishing detection system on predefined email headers and content.
    """
    print("=== Email Phishing Detection System ===")
    
    # Load model and tokenizer
    print("\nLoading model and tokenizer...")
    try:
        model_path = "lstm_spam_model_50.h5"
        tokenizer_path = "lstm_tokenizer_50.pkl"
        model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
        print("Model and tokenizer loaded successfully.")
    except Exception as e:
        print(f"Error loading model or tokenizer: {e}")
        print("Make sure the model and tokenizer files exist in the current directory.")
        return
    
    # Generate and display report
    print("\nAnalyzing email...")
    try:
        report, verdict, confidence = generate_report(email_headers, email_content, model, tokenizer)
        print(report)
        
        # Visual indicator of verdict
        if "PHISHING" in verdict.upper():
            print("\n⚠️  WARNING: This email shows phishing characteristics! Be cautious!")
        elif "SUSPICIOUS" in verdict.upper():
            print("\n⚠️  CAUTION: This email contains some suspicious elements.")
        else:
            print("\n✅  This email appears to be legitimate.")
        
        # Enhance the report using Groq API
        print("\nEnhancing report with Groq API...")
        enhanced_report = enhance_report_with_groq(report, verdict, confidence)
        print("\n=== Enhanced Report ===")
        print(enhanced_report)
        
        return report, verdict, confidence, enhanced_report
                
    except Exception as e:
        print(f"Error during analysis: {e}")

# ----------------------------
# # Main Function
# # ----------------------------
# if __name__ == "__main__":
#     # Define email headers and content
#     email_headers = """
#     From: bankalerts@kotak.com
#     Reply-To: bankalerts@kotak.com
#     ARC-Authentication-Results: i=1; mx.google.com;
#        dkim=pass header.i=@kotak.com header.s=Outgoing01 header.b=jbnHPD4n;
#        spf=pass (google.com: domain of bankalerts@kotak.com designates 121.241.26.42 as permitted sender) smtp.mailfrom=bankalerts@kotak.com;
#        dmarc=pass (p=REJECT sp=REJECT dis=NONE) header.from=kotak.com
#     """
#     email_content = """
# Congratulations! You've won a $1000 Walmart gift card. Go to http://bit.ly/fake-link to claim now.
# This is a limited-time offer, so act fast!
#     """
    
#     # Run the phishing detector
#     report, verdict, confidence, enhanced_report = run_phishing_detector(email_headers, email_content)