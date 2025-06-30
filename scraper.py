import praw
import config

def fetch_reddit_posts():
    reddit = praw.Reddit(
        client_id=config.CLIENT_ID,
        client_secret=config.CLIENT_SECRET,
        user_agent=config.USER_AGENT
    )
    subreddit = reddit.subreddit("wallstreetbets")
    for post in subreddit.hot(limit=10):
        print(post.title)