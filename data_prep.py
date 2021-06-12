'''
Module containing functions used for query normalization and snippet preprocessing.
'''

import re
import math
from collections import Counter


def normalize_query(query):
    '''
    Transforms the query into a list of uppercase keywords.
    Return the list.
    '''

    keywords = query.upper().split()
    return keywords


def get_sentence_set(snippets, stop_words):
    '''
    Normalizes the snippets and splits them into sentences according
    to standard punctuation, only keeping those with more than 2
    non-stopwords. 
    Returns the list of sentences.
    '''

    # split sentences according to standard punctuation
    sentence_set = list()
    for snipp in snippets:
        sentences = re.split('[,.;:\-?|]', snipp)
        for sentence in sentences:
            if sentence != '':
                if sentence[0] == ' ':
                    sentence_set.append(sentence[1:])
                else:
                    sentence_set.append(sentence)

    # only keep sentences with more than 2 non-stopwords
    final_sentence_set = list()
    for sentence in sentence_set:
        counter = 0
        for word in sentence.split():
            if word not in stop_words:
                counter += 1
        if counter > 2:
            final_sentence_set.append(sentence)
    
    return final_sentence_set


def get_baseline(snippets, stop_words):
    '''
    Calculated the Term Frequency - Inverse Document Frequency for each unique
    snippet of the retrieved snippets. Each snippet is interpreted as one
    document, and all the snippets are seen as the collection of documents. 
    '''

    words = list()
    for snipp in snippets:
        for sentence in re.split('[,.;:\-?|]', snipp):
            for word in sentence.split(' '):
                words.append(word)
    
    unique_words = list(Counter(words).keys())
    unique_words_freq = list(Counter(words).values())

    word_freq = list()
    max_freq = max(unique_words_freq)
    collection_size = len(snippets)

    for i in range(len(unique_words)):
        if unique_words[i] != '' and unique_words[i].lower() not in stop_words and not unique_words[i].isnumeric():
            occurences = 0
            for snipp in snippets:
                if unique_words[i] in snipp:
                    occurences += 1

            tfidf = (unique_words_freq[i] / max_freq) * math.log(collection_size / occurences)
            word_freq.append((unique_words[i], tfidf))

    return word_freq


def get_unigrams(sentence_set, stop_words):
    '''
    Find the words that occur at least 2 times in the set of sentences
    and are not stopwords.
    Returns a list of the words and their frequencies as a list of [word, freq].
    '''

    words = list()
    for sentence in sentence_set:
        for word in sentence.split():
            words.append(word)
    
    unique_words = list(Counter(words).keys())
    unique_words_freq = list(Counter(words).values())

    unigrams = list()
    unigram_freqs = list()
    for i in range(len(unique_words)):
        if unique_words[i] != '' and unique_words[i].lower() not in stop_words and unique_words_freq[i] >= 2:
            unigrams.append([unique_words[i], unique_words_freq[i]])

    return unigrams