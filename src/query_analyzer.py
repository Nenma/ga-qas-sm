'''Module containing a single function used to determine the Estimated Answer Type (EAT) for a given query.'''

import re
from collections import Counter


DATE = ['WHEN', 'WHAT YEAR', 'IN WHAT YEAR', 'WHAT DAY', 'IN WHAT DAY']
LOCATION = ['WHERE',
            'WHAT CITY', 'IN WHAT CITY', 'IN WHICH CITY',
            'WHAT COUNTRY', 'IN WHAT COUNTRY', 'IN WHICH COUNTRY',
            'WHAT TOWN', 'IN WHAT TOWN', 'IN WHICH TOWN',
            'WHAT CONTINENT', 'IN WHAT CONTINENT', 'IN WHICH CONTINENT',
            'WHAT PLANET', 'IN WHAT PLANET', 'IN WHICH PLANET',
            'WHAT REGION', 'IN WHAT REGION', 'IN WHICH REGION',
            'WHAT AREA', 'IN WHAT AREA', 'IN WHICH AREA']
PERSON = ['WHO', 'WHOM', 'WHAT IS THE NAME OF', 'WHAT PERSON', 'WHAT MAN', 'WHAT WOMAN', 'WHAT COMPANY', 'WHAT ENTERPRISE']


def get_EAT(query):
    '''Return the Estimated Answer Type (EAT) of the query as a string'''

    query = query.upper()
    if any([item in query for item in DATE]): return 'DATE'
    if any([item in query for item in LOCATION]): return 'LOCATION'
    if any([item in query for item in PERSON]): return 'PERSON'


def calc_syn_contribution(sentences, answers, max_eps):
    '''
    Calculates syntactic contribution, or the frequency with which words are
    positioned to the left of the answer with 'epsilon' words between them,
    respectively to the right of the answer in the same fashion.
    Returns 2 dictionaries: one corresponding to the 'left frequencies' and
    one corresponding to the 'right frequencies'.
    '''

    for i in range(len(sentences)):
        sentences[i] = sentences[i].replace(answers[i], 'w')
    
    words = list()
    for sentence in sentences:
        for word in sentence.split():
            words.append(word)

    unique_words = list(Counter(words).keys())
    unique_words_freq = list(Counter(words).values())

    # initialize frequency dictionaries for left and right
    Pl = dict()
    Pr = dict()
    for word in unique_words:
        Pl[word] = list()
        Pr[word] = list()

    # use regex to calculate the frequency values
    # rf'{FIRST_WORD}\W+(\w+\W+){{{n}}}{SECOND_WORD}' - regex for matching two words within exactly n words of each other
    for i, word in enumerate(unique_words):
        if word != 'w':
            for eps in range(max_eps):
                left_counter = 0
                right_counter = 0
                for sentence in sentences:
                    left_counter += len(re.findall(rf'{word}\W+(\w+\W+){{{eps}}}w', sentence))
                    right_counter += len(re.findall(rf'w\W+(\w+\W+){{{eps}}}{word}', sentence))
                Pl[word].append(left_counter / unique_words_freq[i])
                Pr[word].append(right_counter / unique_words_freq[i])

    # remove inconsequential entries - that have 0 frequency across the board
    for word, freqs in list(Pl.items()):
        if not any(freqs):
            del Pl[word]
    for word, freqs in list(Pr.items()):
        if not any(freqs):
            del Pr[word]
    
    return Pl, Pr