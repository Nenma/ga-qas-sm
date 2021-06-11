import requests
import json
from nltk.corpus import stopwords

import query_analyzer as qa
import data_prep as dp
import answer_extraction as ae


query = 'who invented the lightbulb'
counter = 10  # number of snippets to be retrieved (max. 10)
stop_words = set(stopwords.words('english'))


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

    # test = open('info/test.txt', 'w')
    # json_response = response.json()
    # for i in range(counter):
    #     snipp = json_response['items'][i]['snippet']
    #     if snipp:
    #         snipp = snipp.strip('\n')
    #         snipp = snipp.replace('\n', '')
    #         test.write(snipp + '\n')

    return response.json()


def read_snippets():
    test = open('info/test.txt', 'r')
    snippets = test.readlines()

    # normalize snippets (~)
    normalized_snippets = [snipp.strip().upper().encode('ascii', 'ignore').decode() for snipp in snippets]

    return normalized_snippets


if __name__ == '__main__':
    # resp = get_raw_snippets()
    eat = qa.get_EAT(query)
    sents, answs = ae.use_qa_store(eat)
    pl, pr = ae.calc_syn_contribution(sents, answs)
    
    snippets = read_snippets()
    sentence_set = dp.get_sentence_set(snippets, stop_words)
    # unigrams = dp.get_unigrams(sent_set)
    # print(unigrams)