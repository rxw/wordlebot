#!/bin/python3

import tweepy
import logging
import time
import datetime
import random

GSQUARE = "🟩"
YSQUARE = "🟨"
BSQUARE = "⬛"

WORDFILE = "sgb-words.txt"
words = set(open(WORDFILE, "r").read().split("\n")[:-1])
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

playing = {}

def create_api():
    consumer_key = os.getenv("CONSUMER_KEY")
    consumer_secret = os.getenv("CONSUMER_SECRET")
    access_token = os.getenv("ACCESS_TOKEN")
    access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth, wait_on_rate_limit=True, 
        wait_on_rate_limit_notify=True)
    try:
        api.verify_credentials()
    except Exception as e:
        logger.error("Error creating API", exc_info=True)
        raise e
    logger.info("API created")
    return api

def word_emoji_match(w1, w2):
    response = [BSQUARE for i in range(5)]
    w2s = set(w2)
    for i in range(5):
        if w1[i] == w2[j]:
            response[i] = GSQUARE
        elif w1[i] in w2s:
            response[i] = YSQUARE

    return "".join(response)

def check_mentions(api, since_id):
    logger.info("Retrieving mentions")
    new_since_id = since_id
    for tweet in tweepy.Cursor(api.mentions_timeline,
        since_id=since_id).items():
        new_since_id = max(tweet.id, new_since_id)
        if tweet.in_reply_to_status_id is not None:
            continue

        seed = datetime.today().isoformat()
        random.seed(seed)
        todays_word = random.choice(words)

        text = tweet.text.lower().split(" ")
        if len(text) != 2 or not (text[1] in words):
            api.update_status(
                status="Invalid try",
                in_reply_to_status_id=tweet.id,
            )
            continue
        
        word = text[1]
        todayinlist = todays_word.split()
        wordinlist = word.split()
        response = word_emoji_match(todayinlist, wordinlist)

        if tweet.user.id in playing:
            playing[tweet.user.id] += 1
            api.update_status(
                status=response,
                in_reply_to_status_id=tweet.id,
            )
            continue
        else:
            playing[tweet.user.id], number = 1, 1
            api.update_status(
                status=response,
                in_reply_to_status_id=tweet.id,
            )
            continue
        
    return new_since_id

def main():
    api = create_api()
    since_id = 1
    while True:
        since_id = check_mentions(api, since_id)
        logger.info("Waiting...")
        time.sleep(60)

if __name__ == "__main__":
    main()