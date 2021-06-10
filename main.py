import requests
import json
from nltk.corpus import stopwords

import query_analyzer as qa
import data_prep as dp


query = 'who invented the radio'
counter = 10  # number of snippets to be retrieved (max. 10)


def get_raw_snippets():
    '''Calls Google's Custom Search API to search for snippets to the query.'''

    keys_json = open('config/keys.json', 'r').read()
    keys = json.loads(keys_json)
    cx_key = keys['cx_key']
    api_key = keys['api_key']

    response = requests.get(
        'https://customsearch.googleapis.com/customsearch/v1',
        params={'cx': cx_key,
                'lr': 'lang_en',
                'num': counter,
                'q': query,
                'key': api_key}
    )

    # json_response = response.json()
    # for i in range(counter):
    #     snipp = json_response['items'][i]['snippet']
    #     if snipp:
    #         snipp = snipp.strip('\n')
    #         snipp = snipp.replace('\n', '')
    #         test.write(snipp + '\n')

    return response.json()


if __name__ == '__main__':
    eat = qa.get_EAT(query)
    print(dp.normalize_query(query, eat))

    sent_set = dp.get_sentence_set()
    unigrams = dp.get_unigrams(sent_set)
    print(unigrams)