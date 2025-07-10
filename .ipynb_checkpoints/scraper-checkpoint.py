import praw
import config
import requests
import json
import pandas as pd
import numpy as np




headers = {
    "User-Agent": "RedditStockScraper (samadrafpro@gmail.com)"
}

response = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers)
dictionary = response.json()
tickers = pd.DataFrame((entry["ticker"] for entry in dictionary.values()))
print(tickers)


def fetch_reddit_posts():
    reddit = praw.Reddit(
        client_id=config.clientID,
        client_secret=config.clientSecret,
        user_agent=config.userAgent,
        username = config._username,
        password = config._password

    )
    subreddit = reddit.subreddit("wallstreetbets")
    for comment in subreddit.stream.comments():
        for ticker in tickers:
            if (ticker in comment.body):
                print(ticker)



