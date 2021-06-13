'''Module containing functions that make calls to the Twitter API.'''

import requests
import json


TW_API_URL = 'https://api.twitter.com/2/tweets/search/recent'


def get_headers():
    '''Returns the headers for the Twitter API request calls.'''

    keys_json = open('config/keys.json', 'r').read()
    keys = json.loads(keys_json)

    tw_bearer_token = keys['tw_bearer_token']
    headers = {'Authorization': 'Bearer {}'.format(tw_bearer_token)}

    return headers


def get_og_posts(content, count):
    '''
    Calls the Twitter API to get a max of 'count' recent tweets that are
    relevant to the 'content'.
    Returns the associated JSON object.
    '''

    headers = get_headers()
    response = requests.get(
        TW_API_URL,
        headers=headers,
        params={
            'query': '{} lang:en is:verified -is:reply -is:retweet'.format(content),
            'tweet.fields': 'author_id,conversation_id,lang,public_metrics',
            'max_results': count
        }
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()


def get_replies(conv_id):
    '''
    Calls the Twitter API to get the max of 100 replies to the tweet
    speicifed by 'conv_id'.
    Returns the associated JSON object.
    '''

    headers = get_headers()
    response = requests.get(
        TW_API_URL,
        headers=headers,
        params={
            'query': 'conversation_id:{}'.format(conv_id),
            'tweet.fields': 'in_reply_to_user_id,author_id,conversation_id,lang',
            'max_results': 100
        }
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()


# FOR TESTING
if __name__ == '__main__':
    og_posts = get_og_posts('corona virus', 10)
    # test = open('test/test.json', 'w')
    # test.write(json.dumps(og_post, indent=4, sort_keys=True))
    # test.close()

    # test2 = open('test/test2.json', 'a')
    # test2.write('[')
    replies = list()
    for i in range(10):
        reply_count = og_posts['data'][i]['public_metrics']['reply_count']
        if reply_count > 0:
            conv_id = og_posts['data'][i]['conversation_id']
            reply = get_replies(conv_id)
            replies.append(reply)
            # test2.write(json.dumps(reply, indent=4, sort_keys=True) + ',\n')
    # test2.write('{}]')
    # test2.close()
