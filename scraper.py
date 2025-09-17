import praw
import requests
import pandas as pd
import numpy as np
import re
from pandasgui import show
import matplotlib.pyplot as plt
from transformers import pipeline
import config

# Initialize headers for SEC API request
headers = {
    "User-Agent": "RedditStockScraper (samadrafpro@gmail.com)"
}

def fetch_ticker_list():
    """Fetch and process ticker list from SEC API."""
    try:
        response = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        dictionary = response.json()
        tickers = pd.DataFrame((entry["ticker"] for entry in dictionary.values()), columns=["Ticker"])
        return tickers, [str(ticker) for ticker in tickers["Ticker"]]
    except requests.RequestException as e:
        print(f"Error fetching ticker list: {e}")
        return pd.DataFrame(columns=["Ticker"]), []

def fetch_reddit_posts_and_comments():
    """Fetch Reddit posts and comments, count ticker mentions, and perform sentiment analysis."""
    # Initialize Reddit API client
    try:
        reddit = praw.Reddit(
            client_id=config.clientID,
            client_secret=config.clientSecret,
            user_agent=config.userAgent,
            username=config._username,
            password=config._password
        )
    except Exception as e:
        print(f"Error initializing Reddit client: {e}")
        return pd.DataFrame(columns=["Ticker", "Mentions", "Avg_Sentiment"])

    # Initialize Hugging Face sentiment analysis pipeline
    try:
        sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    except Exception as e:
        print(f"Error initializing sentiment analyzer: {e}")
        return pd.DataFrame(columns=["Ticker", "Mentions", "Avg_Sentiment"])

    # Fetch ticker list
    tickers, ticker_list = fetch_ticker_list()
    if tickers.empty:
        return pd.DataFrame(columns=["Ticker", "Mentions", "Avg_Sentiment"])

    # Initialize data structures
    ticker_counts = {}
    ticker_comments = {ticker: [] for ticker in ticker_list}
    subreddit = reddit.subreddit("wallstreetbets+stocks+investing")
    comment_limit = 100

    # Process hot posts (titles)
    for post in subreddit.hot(limit=99):
        text = post.title
        for ticker in ticker_list:
            if re.search(rf'\b{re.escape(ticker)}\b', text, re.IGNORECASE):
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
                ticker_comments[ticker].append(text)

    # Process streaming comments
    count = 0
    for comment in subreddit.stream.comments(skip_existing=True):
        text = comment.body
        count += 1
        if count >= comment_limit:
            break
        for ticker in ticker_list:
            if re.search(rf'\b{re.escape(ticker)}\b', text, re.IGNORECASE):
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1
                ticker_comments[ticker].append(text)

    # Add mention counts to DataFrame
    tickers["Mentions"] = tickers["Ticker"].map(ticker_counts).fillna(0).astype(int)

    # Perform sentiment analysis
    ticker_sentiments = {}
    for ticker in ticker_list:
        comments = ticker_comments.get(ticker, [])
        if comments:
            sentiments = sentiment_analyzer(comments, truncation=True, max_length=512)
            sentiment_scores = [1 if s['label'] == 'POSITIVE' else -1 for s in sentiments]
            ticker_sentiments[ticker] = np.mean(sentiment_scores) if sentiment_scores else 0
        else:
            ticker_sentiments[ticker] = 0

    # Add sentiment scores to DataFrame
    tickers["Avg_Sentiment"] = tickers["Ticker"].map(ticker_sentiments).fillna(0)

    # Filter tickers with non-zero mentions
    top_tickers = tickers[tickers["Mentions"] > 0].sort_values(by="Mentions", ascending=False)

    # Visualize results
    plt.figure(figsize=(10, 6))
    plt.bar(top_tickers["Ticker"], top_tickers["Avg_Sentiment"], color='skyblue')
    plt.xlabel("Ticker")
    plt.ylabel("Average Sentiment Score (Positive: 1, Negative: -1)")
    plt.title("Sentiment Analysis of Reddit Comments by Stock Ticker")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Display DataFrame with pandasgui
    show(top_tickers)

    return top_tickers

if __name__ == "__main__":
    fetch_reddit_posts_and_comments()