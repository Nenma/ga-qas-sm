'''Module containing utility functions for interacting with the tw_store.csv.'''

import pandas as pd


def use_tw_store(unigrams):
    '''
    Acces the tw_store.csv to get the (sentence, keywords) pairs whose sentences 
    contain the given unigrams.
    Returns the (sentence, keywords) pairs.
    '''

    store = pd.read_csv('data/tw_store.csv', header=1, encoding='utf8', names=['sentence', 'keywords'])
    
    unigram_words = ''
    for unigram in unigrams:
        unigram_words += unigram + '|'
    specific_store = store[store['sentence'].str.contains(unigram_words[:-1])]

    sentences = specific_store['sentence'].to_list()
    keywords = specific_store['keywords'].to_list()

    return sentences, keywords


def add_to_tw_store(sentence, keywords):
    '''
    Adds a new entry to the tw_store.csv after checking that there
    is no duplicate entry.
    '''
    
    store = pd.read_csv('data/tw_store.csv', header=1, encoding='utf8', names=['sentence', 'keywords'])
    entry = sentence + ',' + keywords + '\n'
    with open('data/tw_store.csv', 'a') as tw_store:
        if not ((store['sentence'] == sentence) & (store['keywords'] == keywords)).any():
            print('[Entry added to tw_store!]')
            tw_store.write(entry)
        else:
            print('[Entry already exists.]')
    tw_store.close()