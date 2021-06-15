'''Module containing functions that make calls to the Google Custom Search API.'''

import json
import requests
import re


G_API_URL = 'https://customsearch.googleapis.com/customsearch/v1'


def normalize_snippet(snippet):
    snippet = snippet.strip().upper().encode('ascii', 'ignore').decode()

    # get rid of parantheses, also get rid of commas and colons (with the intention of avoiding appositions)
    # e.g.: the author, born in 1985, wrote the book
    snippet = re.sub('[\(\)\[\],:]', '', snippet)

    # transform intervals of time NUMBER1-NUMBER2 into NUMBER1 TO NUMBER2
    interval_pairs = re.findall(r'([0-9]+)(-[0-9]+)+', snippet)
    for pair in interval_pairs:
        interval = pair[0] + pair[1]
        snippet = re.sub(interval, pair[0] + ' TO ' + pair[1][1:], snippet)
    
    return snippet


def get_raw_snippets(query, count):
    '''
    Calls Google's Custom Search API to search for snippets to the query
    and writes them to a file.
    '''

    keys_json = open('config/keys.json', 'r').read()
    keys = json.loads(keys_json)

    g_cx_key = keys['g_cx_key']
    g_api_key = keys['g_api_key']

    response = requests.get(
        G_API_URL,
        params={'cx': g_cx_key,
                'lr': 'lang_en',
                'num': count,
                'q': query,
                'key': g_api_key
        }
    )

    if response.status_code != 200:
        raise Exception(response.status_code, response.text)

    test = open('data/raw_snippets.txt', 'w')
    json_response = response.json()
    for i in range(count):
        snipp = json_response['items'][i]['snippet']
        if snipp:
            snipp = snipp.strip()
            snipp = snipp.replace('\n', '')
            snipp = normalize_snippet(snipp)
            test.write(snipp + '\n')
    test.close()