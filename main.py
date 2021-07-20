from credentials.credentials import *
import datetime
import pymongo
from collections import Counter
from itertools import chain
import tweepy

client = pymongo.MongoClient("mongodb+srv://Twitter:Sh070708@cluster0.nuqx6.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client['db']
col = db['twitter']

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
bot = tweepy.API(auth)

name = "WxTrending"

day = datetime.datetime.today()
day = f"{day.year}-{('0' if len(str(day.month)) == 1 else '') + str(day.month)}" \
      f"-{('0' if len(str(day.day)) == 1 else '') + str(day.day)}"

for follower in bot.followers(name):
    if name not in bot.followers(follower.screen_name):
        bot.create_friendship(follower.screen_name)

previous_data = col.find_one()
data = col.find_one()

if day not in data.keys():
    data[day] = {}

cur_time = datetime.datetime.now().__str__()

for tweet in bot.home_timeline(count=100):
    punctuation = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
    tweet_text = tweet.text
    for punc in punctuation:
        tweet_text.replace(punc, '').replace('\u2026', '')
    if len(data[day].keys()) == 0:
        if tweet.created_at > datetime.datetime.fromisoformat(day):
            data[day][cur_time].append(tweet_text.split(' '))
    else:
        if tweet.created_at > datetime.datetime.fromisoformat((keys_of_json := list(data[day].keys()))[keys_of_json.index(cur_time) - 1]):
            data[day][cur_time].append(tweet_text.split(' '))




if datetime.datetime.now() > datetime.datetime.now().replace(hour=23, minute=43):
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

col.update_one(previous_data, {'$setx': data})
