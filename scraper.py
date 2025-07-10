import praw
import config
import requests
import json
import pandas as pd
import numpy as np
import re
from pandasgui import show



headers = {
    "User-Agent": "RedditStockScraper (samadrafpro@gmail.com)"
}

response = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
dictionary = response.json()
tickers = pd.DataFrame((entry["ticker"] for entry in dictionary.values()))
tickers.columns = ["Ticker"]
ticker_list = [str(row[0]) for row in tickers.values]



def fetch_reddit_posts():
    reddit = praw.Reddit(
        client_id=config.clientID,
        client_secret=config.clientSecret,
        user_agent=config.userAgent,
        username = config._username,
        password = config._password

    )
    subreddit = reddit.subreddit("wallstreetbets+stocks+investing")
    ticker_counts = {}

    for posts in subreddit.hot(limit = 99):
        text = posts.title
        words = text.split()
        for ticker in ticker_list:
            if re.search(rf'\b{re.escape(ticker)}\b', text):
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

    comment_limit = 100
    count = 0
    for comment in subreddit.stream.comments(skip_existing=True):
        text = comment.body
        count +=1
        if count >= comment_limit:
            break
        for ticker in ticker_list:
            if re.search(rf'\b{re.escape(ticker)}\b', text):
                ticker_counts[ticker] = ticker_counts.get(ticker, 0) + 1

    tickers["Mentions"] = tickers["Ticker"].map(ticker_counts).fillna(0).astype(int)
    show(tickers)