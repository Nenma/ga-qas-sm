'''
Module containing the genetic algorithm used for answer extraction.
'''

import re
import pandas as pd
from collections import Counter


def use_qa_store(eat_type):
    '''Acces the qa_store.csv to get the (sentences, aswers) pairs for a certain EAT.'''

    store = pd.read_csv('qa_store.csv', header=1, encoding='utf8', names=['type', 'question', 'sentence', 'answer'])
    specific_store = store[store['type'] == eat_type]
    
    sentences = specific_store['sentence'].to_list()
    answers = specific_store['answer'].to_list()

    return sentences, answers


def calc_syn_contribution(sentences, answers):
    '''
    Calculates syntactic contribution, or the frequency with which words are
    positioned to the left of the answer with 'epsilon' words between them,
    respectively to the right of the answer in the same fashion.
    Returns 2 dictionaries: one corresponding to the 'left frequencies' and
    one corresponding to the 'right frequencies'.
    '''

    for i in range(len(sentences)):
        sentences[i] = sentences[i].replace(answers[i], 'w')
    
    words = []
    for sentence in sentences:
        for word in sentence.split(' '):
            words.append(word)

    unique_words = list(Counter(words).keys())
    unique_words_freq = list(Counter(words).values())

    # find the length of the longest sentence, thus obtaining the maximum number of words between 2 words
    split_sentences = [sentence.split() for sentence in sentences]
    max_sent_len = len(max(split_sentences, key=lambda x: len(x)))
    max_eps = max_sent_len - 2

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

    return Pl, Pr


def create_initial_pop(pop_size, sentences, stopwords):
    pass


def crossover(pop, prob):
    pass


def mutate(pop, prob):
    pass


def evaluate_pop(pop, Pl, Pr):
    pass


def select_pop(pop, fitness):
    pass


def ga(generations, sentences, pop_size, stopwords, mutation_prob, crossover_prob, Pl, Pr):
    pop = create_initial_pop(pop_size, sentences, stopwords)

    for _ in range(generations):
        pop = crossover(pop, crossover_prob)
        pop = mutate(pop, mutation_prob)
        fitness = evaluate_pop(pop, Pl, Pr)
        pop = select_pop(pop, fitness)

    return pop[0]