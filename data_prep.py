'''
Module containing functions used for query normalization and snippet preprocessing.
'''

import re
from nltk.corpus import stopwords
from collections import Counter


stop_words = set(stopwords.words('english'))


def normalize_query(query, eat):
    '''
    Transforms the query into a tuple of EAT and a tuple of keywords.
    Return the transformed query.
    '''

    keywords = tuple([word for word in query.split(' ') if word.lower() not in stop_words])
    return (eat, keywords)


def get_sentence_set():
    '''
    Normalizes the snippets and splits them into sentences according
    to standard punctuation, only keeping those with more than 2
    non-stopwords. 
    Returns the list of sentences.
    '''

    test = open('info/test.txt', 'r')
    snippets = test.readlines()

    # normalize snippets (~)
    normalized_snippets = [snipp.strip().upper().encode('ascii', 'ignore').decode() for snipp in snippets]

    # split sentences according to standard punctuation
    sentence_set = []
    for snipp in normalized_snippets:
        sents = re.split('[,.;:\-?|]', snipp)
        for sent in sents:
            if sent != '':
                if sent[0] == ' ':
                    sentence_set.append(sent[1:])
                else:
                    sentence_set.append(sent)

    # only keep sentences with more than 2 non-stopwords
    final_sentence_set = []
    for sent in sentence_set:
        counter = 0
        for word in sent.split(' '):
            if word not in stop_words:
                counter += 1
        if counter > 2:
            final_sentence_set.append(sent)
    
    return final_sentence_set


def get_unigrams(sentence_set):
    '''
    Find the words that occur at least 2 times in the set of sentences
    and are not stopwords.
    Returns a list of tuples of words with their frequency.
    '''

    words = []
    for sent in sentence_set:
        for word in sent.split(' '):
            words.append(word)
    
    unique_words = list(Counter(words).keys())
    unique_words_freq = list(Counter(words).values())

    unigrams = []
    for i in range(len(unique_words)):
        if unique_words[i] != '' and unique_words[i].lower() not in stop_words and unique_words_freq[i] >= 2:
            unigrams.append((unique_words[i], unique_words_freq[i]))

    return unigrams