import praw
import config
import json




def fetch_reddit_posts():
    reddit = praw.Reddit(
        client_id=config.clientID,
        client_secret=config.clientSecret,
        user_agent=config.userAgent,
        username = config._username,
        password = config._password

    )
    subreddit = reddit.subreddit("wallstreetbets")
    #all_comments = subreddit.comments.list()
    with open("submissions.txt", "w", encoding="utf-8") as file:
        for submission in subreddit.top(limit=10):
            file.write(submission.title + "\n")
    for post in subreddit.hot(limit = 10):
        for comment in subreddit.stream.comments():
            print(comment.body)

