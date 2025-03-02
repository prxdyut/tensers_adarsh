import numpy as np
import pandas as pd
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense, Dropout
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# ----------------------------
# 1. Load and Concatenate Datasets
# ----------------------------
# Load the first dataset
df1 = pd.read_csv("/kaggle/input/phishing-dataset/Phishing_Email.csv")
# Drop the 'Unnamed: 0' column if it exists
if 'Unnamed: 0' in df1.columns:
    df1 = df1.drop(columns=['Unnamed: 0'])

# Load the second dataset
df2 = pd.read_csv("/kaggle/input/phishing-dataset/Phishing_validation_emails.csv")

# Concatenate the two datasets
combined_df = pd.concat([df1, df2], ignore_index=True)

# Rename columns for consistency (if necessary)
combined_df.columns = ['Email Text', 'Email Type']

# ----------------------------
# 2. Clean the Dataset
# ----------------------------
# Check for NaN values in the 'Email Text' column
print("Number of NaN values in 'Email Text':", combined_df['Email Text'].isna().sum())

# Drop rows with NaN values in 'Email Text'
combined_df = combined_df.dropna(subset=['Email Text'])

# Alternatively, fill NaN values with a placeholder (e.g., "unknown")
# combined_df['Email Text'] = combined_df['Email Text'].fillna("unknown")

# ----------------------------
# 3. Preprocess the Combined Dataset
# ----------------------------
# Encode labels (Safe Email: 0, Phishing Email: 1)
label_encoder = LabelEncoder()
combined_df['Email Type'] = label_encoder.fit_transform(combined_df['Email Type'])

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(
    combined_df['Email Text'], combined_df['Email Type'], test_size=0.2, random_state=42
)

# ----------------------------
# 4. Tokenize and Pad Sequences
# ----------------------------
# Tokenize the text data
tokenizer = Tokenizer(num_words=10000)  # Adjust num_words based on your dataset size
tokenizer.fit_on_texts(X_train)

# Convert text to sequences
X_train_sequences = tokenizer.texts_to_sequences(X_train)
X_test_sequences = tokenizer.texts_to_sequences(X_test)

# Pad sequences to ensure uniform input size
max_sequence_length = 100  # Adjust based on your dataset
X_train_padded = pad_sequences(X_train_sequences, maxlen=max_sequence_length, padding='post', truncating='post')
X_test_padded = pad_sequences(X_test_sequences, maxlen=max_sequence_length, padding='post', truncating='post')

# ----------------------------
# 5. Build the LSTM Model
# ----------------------------
# Define model parameters
vocab_size = len(tokenizer.word_index) + 1  # Vocabulary size
embedding_dim = 128  # Dimension of word embeddings
lstm_units = 64  # Number of LSTM units
dropout_rate = 0.5  # Dropout rate

# Build the model
model = Sequential()
model.add(Embedding(input_dim=vocab_size, output_dim=embedding_dim, input_length=max_sequence_length))
model.add(LSTM(lstm_units, return_sequences=False))
model.add(Dropout(dropout_rate))
model.add(Dense(1, activation='sigmoid'))  # Binary classification (spam or not spam)

# Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Print model summary
model.summary()

# ----------------------------
# 6. Train the LSTM Model
# ----------------------------
# Train the model
batch_size = 64
epochs = 50  # Adjust based on your dataset size and computational resources

history = model.fit(
    X_train_padded,
    y_train,
    batch_size=batch_size,
    epochs=epochs,
    validation_data=(X_test_padded, y_test),
    verbose=1
)

# ----------------------------
# 7. Evaluate the Model
# ----------------------------
# Evaluate on the test set
loss, accuracy = model.evaluate(X_test_padded, y_test, verbose=1)
print(f"Test Accuracy: {accuracy:.4f}")

# ----------------------------
# 8. Save the Model and Tokenizer
# ----------------------------
# Save the trained model
model.save("lstm_spam_model_50.h5")

# Save the tokenizer (for preprocessing new emails)
import pickle
with open("lstm_tokenizer_50.pkl", "wb") as f:
    pickle.dump(tokenizer, f)

print("Model and tokenizer saved successfully!")