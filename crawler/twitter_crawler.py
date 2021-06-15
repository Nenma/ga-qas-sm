'''Module containing functions that make calls to the Twitter API.'''

import requests
import json
import re


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
            'query': '\"{}\" lang:en -is:reply -is:retweet'.format(content),
            'max_results': count
        }
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()


def normalize_post(post):
    '''Returns the normalized post.'''

    post = post.strip().replace('\n', ' ')
    post = post.upper().encode('ascii', 'ignore').decode()
    post = re.sub('[\(\)\[\],]', '', post)

    return post


def get_raw_posts(query, count):
    '''
    Calls Twitter's API to search for posts related to the query
    and writes them to a file.
    '''

    og_posts_json = get_og_posts(query, count)

    posts = open('data/raw_posts.txt', 'w', encoding='utf8')
    for i in range(count):
        post = og_posts_json['data'][i]['text']
        post = normalize_post(post)
        posts.write(post + '\n')
    posts.close()
