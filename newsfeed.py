from transformers import pipeline
import feedparser
import sys
import requests
from bs4 import BeautifulSoup

if not sys.warnoptions:
    import warnings
    warnings.simplefilter("ignore")

# Load the pre-trained sentiment analysis model for financial news
sentiment_model = pipeline("sentiment-analysis", model="ProsusAI/finbert")  # Sentiment analysis for financial news

# Load a summarization model (e.g., BART)
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")  # Replace with Mistral if available

# Fetch real-time news using CyberScoop RSS feed
RSS_FEED = "https://www.cyberscoop.com/feed/"

def fetch_news(rss_url):
    """Fetches news articles from the CyberScoop RSS feed."""
    news = feedparser.parse(rss_url)
    return [(entry.title, entry.link) for entry in news.entries]

def analyze_sentiment(text):
    """Analyzes the sentiment of the cybersecurity news."""
    sentiment = sentiment_model(text)
    return sentiment[0]['label'], sentiment[0]['score']

def extract_text_from_url(url):
    """Extracts the main text content from a news article URL."""
    # Send a GET request to the article URL
    response = requests.get(url)
    response.raise_for_status()  # Raise an exception for HTTP errors
    
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract all text from the webpage
    text = soup.get_text(separator=' ', strip=True)
    return text

def summarize_text(text, max_length=150, min_length=50):
    """Summarizes the text using the summarization model."""
    try:
        # Truncate text to avoid exceeding the model's token limit
        max_input_length = 1024  # Adjust based on the model's token limit
        truncated_text = text[:max_input_length]
        
        # Generate the summary
        summary = summarizer(truncated_text, max_length=max_length, min_length=min_length, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"Error summarizing text: {e}")
        return None

def main():
    print(f"\n=== News from CyberScoop ===")
    try:
        news_items = fetch_news(RSS_FEED)
        for title, link in news_items[:5]:  # Limit to 5 articles for demonstration
            print(f"Title: {title}")
            print(f"Link: {link}")

            # Extract the full article content
            full_text = extract_text_from_url(link)
            if full_text:
                # Summarize the full text
                summarized_news = summarize_text(full_text)
                if summarized_news:
                    print(f"Summary: {summarized_news}")

                    # Analyze sentiment of the summary
                    sentiment, probability = analyze_sentiment(summarized_news)
                    print(f"Sentiment: {sentiment} (Probability: {probability:.4f})")

                    # Assess whether the news is bullish, bearish, or neutral
                    if sentiment == "positive":
                        print("This news could be bullish.")
                    elif sentiment == "negative":
                        print("This news could be bearish.")
                    else:
                        print("This news seems neutral.")
                else:
                    print("Failed to summarize the article.")
            else:
                print("Could not extract the article content.")
            print("-" * 80)
    except Exception as e:
        print(f"Error processing CyberScoop feed: {e}")

if __name__ == "__main__":
    main()