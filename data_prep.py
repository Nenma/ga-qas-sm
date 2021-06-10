'''
Module containing functions used for query normalization and snippet preprocessing.
'''

import re
import math
from nltk.corpus import stopwords
from collections import Counter


stop_words = set(stopwords.words('english'))


# def normalize_query(query, eat):
#     '''
#     Transforms the query into a tuple of EAT and a tuple of keywords.
#     Return the transformed query.
#     '''

#     keywords = tuple([word for word in query.split(' ') if word.lower() not in stop_words])
#     return (eat, keywords)


def get_sentence_set(snippets):
    '''
    Normalizes the snippets and splits them into sentences according
    to standard punctuation, only keeping those with more than 2
    non-stopwords. 
    Returns the list of sentences.
    '''

    # split sentences according to standard punctuation
    sentence_set = []
    for snipp in snippets:
        sentences = re.split('[,.;:\-?|]', snipp)
        for sentence in sentences:
            if sentence != '':
                if sentence[0] == ' ':
                    sentence_set.append(sentence[1:])
                else:
                    sentence_set.append(sentence)

    # only keep sentences with more than 2 non-stopwords
    final_sentence_set = []
    for sentence in sentence_set:
        counter = 0
        for word in sentence.split(' '):
            if word not in stop_words:
                counter += 1
        if counter > 2:
            final_sentence_set.append(sentence)
    
    return final_sentence_set


def get_baseline(snippets):
    '''
    Calculated the Term Frequency - Inverse Document Frequency for each unique
    snippet of the retrieved snippets. Each snippet is interpreted as one
    document, and all the snippets are seen as the collection of documents. 
    '''

    words = []
    for snipp in snippets:
        for sentence in re.split('[,.;:\-?|]', snipp):
            for word in sentence.split(' '):
                words.append(word)
    
    unique_words = list(Counter(words).keys())
    unique_words_freq = list(Counter(words).values())

    word_freq = []
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


def get_unigrams(sentence_set):
    '''
    Find the words that occur at least 2 times in the set of sentences
    and are not stopwords.
    Returns a list of tuples of words with their frequency.
    '''

    words = []
    for sentence in sentence_set:
        for word in sentence.split(' '):
            words.append(word)
    
    unique_words = list(Counter(words).keys())
    unique_words_freq = list(Counter(words).values())

    unigrams = []
    for i in range(len(unique_words)):
        if unique_words[i] != '' and unique_words[i].lower() not in stop_words and unique_words_freq[i] >= 2:
            unigrams.append((unique_words[i], unique_words_freq[i]))

    return unigrams