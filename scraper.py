import praw
import config






def fetch_reddit_posts():
    reddit = praw.Reddit(
        client_id=config.clientID,
        client_secret=config.clientSecret,
        user_agent=config.userAgent,
        username = config._username,
        password = config._password

    )
    with open("submissions.txt", "w", encoding="utf-8") as file:
        for submission in reddit.subreddit("wallstreetbets").hot(limit=10):
            file.write(submission.title + "\n")


