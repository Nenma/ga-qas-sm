'''Module containing utility funtions for interacting with the qa_store.csv.'''

import pandas as pd


def use_qa_store(eat_type, unigrams):
    '''
    Acces the qa_store.csv to get the (sentence, answer) pairs for a certain EAT
    whose sentences contain the given unigrams.
    Returns the (sentence, answer) pairs.
    '''

    store = pd.read_csv('data/qa_store.csv', header=1, encoding='utf8', names=['type', 'question', 'sentence', 'answer'])
    
    specific_store = store[store['type'] == eat_type]
    
    unigram_words = ''
    for unigram in unigrams:
        unigram_words += unigram + '|'
    specific_store = specific_store[specific_store['sentence'].str.contains(unigram_words[:-1])]

    sentences = specific_store['sentence'].to_list()
    answers = specific_store['answer'].to_list()

    return sentences, answers


def add_to_qa_store(eat_type, query, sentence, answer):
    '''
    Adds a new entry to the qa_store.csv after checking that there
    is no duplicate entry.
    '''
    
    store = pd.read_csv('data/qa_store.csv', header=1, encoding='utf8', names=['type', 'question', 'sentence', 'answer'])
    entry = eat_type + ',' + query + ',' + sentence + ',' + answer + '\n'
    with open('data/qa_store.csv', 'a') as qa_store:
        if not ((store['type'] == eat_type) & (store['question'] == query) & (store['sentence'] == sentence) & (store['answer'] == answer)).any():
            print('[Entry added to qa_store!]')
            qa_store.write(entry)
        else:
            print('[Entry already exists.]')
    qa_store.close()