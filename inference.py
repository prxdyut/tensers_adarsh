import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

def load_model_and_tokenizer(model_path, tokenizer_path):
    """
    Load the trained model and tokenizer
    """
    # Load the model
    model = load_model(model_path)
    
    # Load the tokenizer
    with open(tokenizer_path, 'rb') as f:
        tokenizer = pickle.load(f)
    
    return model, tokenizer

def preprocess_text(text, tokenizer, max_length=100):
    """
    Preprocess a single text input for prediction
    """
    # Convert to sequence
    sequence = tokenizer.texts_to_sequences([text])
    
    # Pad the sequence
    padded_sequence = pad_sequences(sequence, maxlen=max_length, padding='post', truncating='post')
    
    return padded_sequence

def predict_phishing(text, model, tokenizer, max_length=100):
    """
    Predict if an email is a phishing attempt
    """
    # Preprocess the text
    processed_text = preprocess_text(text, tokenizer, max_length)
    
    # Make prediction
    prediction = model.predict(processed_text)[0][0]
    
    # Return prediction and confidence
    is_phishing = bool(prediction >= 0.5)
    confidence = prediction if is_phishing else 1 - prediction
    
    return is_phishing, confidence

# Example usage
if __name__ == "__main__":
    # Paths to saved model and tokenizer
    model_path = "lstm_spam_model_50.h5"
    tokenizer_path = "lstm_tokenizer_50.pkl"
    
    # Load model and tokenizer
    model, tokenizer = load_model_and_tokenizer(model_path, tokenizer_path)
    
    # Get user input
    print("Enter an email text to check if it's a phishing attempt:")
    user_input = input()
    
    # Make prediction
    is_phishing, confidence = predict_phishing(user_input, model, tokenizer)
    
    # Print results
    if not is_phishing:
        print(f"⚠️ This is likely a PHISHING email (confidence: {confidence:.2%})")
    else:
        print(f"✅ This is likely a SAFE email (confidence: {confidence:.2%})")
    