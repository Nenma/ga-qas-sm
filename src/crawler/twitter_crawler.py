'''Module containing functions that make calls to the Twitter API.'''

import sys
import os
import json
import requests
import re


TW_API_URL = 'https://api.twitter.com/2/tweets/search/recent'
TW_API_URL_TRENDS = 'https://api.twitter.com/1.1/trends/place.json'


def get_headers():
    '''Returns the headers for the Twitter API request calls.'''

    keys_json = open('config/keys.json', 'r').read()
    keys = json.loads(keys_json)

    tw_bearer_token = keys['tw_bearer_token']
    headers = {'Authorization': 'Bearer {}'.format(tw_bearer_token)}

    return headers


def get_trends():
    headers = get_headers()
    response = requests.get(
        TW_API_URL_TRENDS,
        headers=headers,
        params={'id': 1}
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    trends = list()
    for item in response.json()[0]['trends']:
        if item['name'].isascii():
            trends.append(item['name'])

    return trends


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
            'query': '\"{}\" lang:en -is:reply -is:retweet -has:links'.format(content),
            'max_results': count
        }
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    return response.json()


def normalize_post(post):
    '''Returns the normalized post.'''

    post = post.strip().replace('\n', ' ')
    
    # get rid of special characters
    post = post.upper().encode('ascii', 'ignore').decode()
    
    # get rid of hyperlinks
    post = re.sub(r'HTTPS?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)', '', post)
    
    # get rid of parantheses and commans and colons
    post = re.sub('[\(\)\[\],:]', '', post)

    return post


def get_raw_posts(query, count):
    '''
    Calls Twitter's API to search for posts related to the query
    and writes them to a file.
    '''

    og_posts_json = get_og_posts(query, count)

    posts = list()
    # file = open('data/raw_data.txt', 'w', encoding='utf8')
    for i in range(count):
        post = og_posts_json['data'][i]['text']
        post = normalize_post(post)
        posts.append(post)
        # file.write(post + '\n')
    # file.close()

    return posts


if __name__ == '__main__':
    test = get_trends()
    print(test)