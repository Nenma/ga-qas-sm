'Main module.'

import json
import random
import tweepy

import crawler.twitter_crawler as tc
import controller


def get_tweet():
    possible_trends = tc.get_trends()
    selected_trend = random.choice(possible_trends)
    selected_tweet = controller.get_selected_tweet(selected_trend)

    return selected_tweet


def post_tweet():
    print('Get credentials')
    keys_json = open('config/keys.json', 'r').read()
    keys = json.loads(keys_json)
    consumer_key = keys['tw_consumer_key']
    consumer_secret = keys['tw_consumer_secret']
    access_token = keys['tw_access_token']
    access_token_secret = keys['tw_access_token_secret']

    print('Authenticate')
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    print('Get tweet')
    tweet = get_tweet()

    print(f'Post tweet: {tweet}')
    api.update_status('[GA-QAS-SM Bot]\n\n' + tweet)


if __name__ == '__main__':
    post_tweet()