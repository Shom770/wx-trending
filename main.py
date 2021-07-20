from credentials.credentials import *
import datetime
import pymongo
from time import sleep
from collections import Counter
from itertools import chain
import tweepy


def update_bot():
    try:
        client = pymongo.MongoClient(
            "mongodb+srv://Twitter:Sh070708@cluster0.nuqx6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = client['db']
        col = db['twitter']
        try:
            file = open("words_to_remove.txt", "r")
            words_to_remove = [line.strip() for line in file]
        finally:
            file.close()

        words_to_remove = set(words_to_remove)

        auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
        bot = tweepy.API(auth)

        day = datetime.datetime.today()
        day = f"{day.year}-{('0' if len(str(day.month)) == 1 else '') + str(day.month)}" \
              f"-{('0' if len(str(day.day)) == 1 else '') + str(day.day)}"

        if col.find_one() is None:
            col.insert_one({
            })
        previous_data = col.find_one()
        data = col.find_one()

        if day not in data.keys():
            data[day] = {}

        cur_time = datetime.datetime.now().__str__()

        data[day][cur_time] = []

        for tweet in bot.home_timeline(count=75):
            punctuation = "!()-[]{};:'\",<>./?@#$%^&*_~"
            tweet_text = tweet.text.lower()[2:] if 'rt' in tweet_text else tweet.text.lower()
            if 'continues' in tweet_text or 'issues' in tweet_text or 'severe' in tweet_text or 'warning' in tweet_text or 'advisory' in tweet_text:
                pass
            else:
                for punc in punctuation:
                    tweet_text = tweet_text.replace(punc, '')

                tweet_text = tweet_text.split(' ')
                tweet_text = list(set(tweet_text) - words_to_remove)

                if len(data[day].keys()) == 0:
                    if tweet.created_at > datetime.datetime.fromisoformat(day):
                        data[day][cur_time].append(tweet_text)
                else:
                    if tweet.created_at > datetime.datetime.fromisoformat((keys_of_json := list(data[day].keys()))
                                                                          [keys_of_json.index(cur_time) - 1]):
                        data[day][cur_time].append(tweet_text)

        if datetime.datetime.now().replace(hour=23, minute=43) < datetime.datetime.now() < \
                datetime.datetime.now().replace(hour=23, minute=49):
            trending_words = 'Trending Today:\n'
            tweets_of_today = []
            for key in data[day].keys():
                if data[day][key]:
                    tweets_of_today.append(*data[day][key])

            tweets_of_today = chain.from_iterable(tweets_of_today)

            tweets_of_today = Counter(tweets_of_today)
            tweets_of_today = dict(tweets_of_today.most_common(10))

            for key, val in zip(tweets_of_today.keys(), tweets_of_today.values()):
                trending_words += f'{key} [used {val} times]\n---\n'

            bot.update_status(trending_words)

        col.update_one(previous_data, {'$set': data}, upsert=True)
    except tweepy.error.RateLimitError:
        print('error!')


while True:
    update_bot()
    sleep(900)
