import os

TWITTER_CONSUMER_KEY: str = os.environ.get(
    'TWITTER_CONSUMER_KEY', '/twitter/consumer_key')
TWITTER_CONSUMER_SECRET: str = os.environ.get(
    'TWITTER_CONSUMER_SECRET', '/twitter/consumer_secret')
TWITTER_ACCESS_TOKEN: str = os.environ.get(
    'TWITTER_ACCESS_TOKEN', 'twitter/access_token')
TWITTER_ACCESS_TOKEN_SECRET: str = os.environ.get(
    'TWITTER_ACCESS_TOKEN_SECRET', '/twitter/access_token_secret')

TWEET_DATA_TABLE = os.environ.get(
    'TWEET_DATA_TABLE', 'TweetData')