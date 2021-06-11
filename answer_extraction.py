'''
Module containing the genetic algorithm used for answer extraction.
'''

from hashlib import new
import re
import pandas as pd
import random
from collections import Counter


def use_qa_store(eat_type):
    '''Acces the qa_store.csv to get the (sentences, aswers) pairs for a certain EAT.'''

    store = pd.read_csv('data/qa_store.csv', header=1, encoding='utf8', names=['type', 'question', 'sentence', 'answer'])
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
    
    words = list()
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

    # remove inconsequential entries - that have 0 frequency across the board
    for word, freqs in list(Pl.items()):
        if not any(freqs):
            del Pl[word]
    for word, freqs in list(Pr.items()):
        if not any(freqs):
            del Pr[word]
    
    return Pl, Pr


def query_weight(word, query):
    '''
    Give more weight to words that are part of the query and 
    are next to an answer candidate.
    '''

    if word in query:
        return 2
    else:
        return 1


# a chromosome is [K, s, k1, k2] where
# K - fitness of answer candidate
# s - sentence index
# k1 - left boundary
# k2 - right boundary
def fitness(chromosome, query, sentence_set, Pl, Pr):
    '''
    The function assigns high fitness to answer candidates that show a highly
    similar syntactic behaviour with answers in the qa_store, with which they
    also share common query terms in the context.
    Returns the chromosome with its assigned fitness.
    '''
    index = chromosome[1]
    k1 = chromosome[2]
    k2 = chromosome[3]

    sentence = sentence_set[index]
    sentence = sentence.split()

    part_sum = 0
    
    # words before the answer candidate
    for i in range(1, k1):
        word = sentence[i]
        part_sum += query_weight(word, query) * Pl[word][i - 1]
    
    # words after the answer candidate:
    for i in range(k2 + 1, len(sentence)):
        word = sentence[i]
        part_sum += query_weight(word, query) * Pr[word][i - k2 - 1]

    chromosome[0] = part_sum

    return chromosome


def create_initial_pop(query, sentence_set, stop_words):
    '''
    Initializes the population with a number of chromosomes equal to the
    size of the sentence set. A chromosome is a list [K, s, k1, k2] where
    K is the initial fitness (0), s is the sentence index, and k1 and k2 
    are the boundaries of the n-gram in the sentence.
    Returns the list of chromosomes.
    '''
    pop = list()
    for i, sentence in enumerate(sentence_set):
        # generate new k1 and k2 if the n-gram contains stopwords or words from the query
        bad_candidate = True
        while bad_candidate:
            bad_candidate = False
            k1 = random.randint(0, len(sentence))
            k2 = random.randint(k1, len(sentence))
            if any([word in sentence[k1:k2] for word in stop_words]) or any([word in sentence[k1:k2] for word in query]):
                bad_candidate = True
        
        pop.append([0, i, k1, k2])

    return pop


# a chromosome is [K, s, k1, k2] where
# K - fitness of answer candidate
# s - sentence index
# k1 - left boundary
# k2 - right boundary
def crossover(pop, prob, query, sentence_set, Pl, Pr):
    '''
    Randomly select 2 chromosomes and create 2 children whose
    k1 and k2 boundaries are a mix of the 2 parents'. Do this
    as many times as there are chromosomes in the population.
    Returns the new population.
    '''
    new_pop = pop[:]
    for _ in range(len(pop)):
        chance = random.uniform(0, 1)
        if chance <= prob:
            first_parent = random.randint(0, len(pop))
            second_parent = random.randint(0, len(pop))
            while second_parent == first_parent:
                second_parent = random.randint(0, len(pop))

            first_parent = pop[first_parent]
            first_index = first_parent[1]
            first_k1 = first_parent[2]
            first_k2 = first_parent[3]

            second_parent = pop[second_parent]
            second_index = second_parent[1]
            second_k1 = second_parent[2]
            second_k2 = second_parent[3]

            b1 = min(first_k1, second_k1)
            b2 = min(max(first_k2, second_k2), len(sentence_set(first_index)))
            b3 = max(first_k1, second_k1)
            b4 = min(max(first_k2, second_k2), b3)

            if b1 < b2 <= len(sentence_set(first_index)) - 1 and b3 < b4 <= len(sentence_set(second_index)) - 1:
                first_child = [0, first_index, b1, b2]
                first_child[0] = fitness(first_child, query, sentence_set, Pl, Pr)
                new_pop.append(first_child)

                second_child = [0, second_index, b3, b4]
                second_child[0] = fitness(second_child, query, sentence_set, Pl, Pr)
                new_pop.append(second_child)

    return new_pop


# a chromosome is [K, s, k1, k2] where
# K - fitness of answer candidate
# s - sentence index
# k1 - left boundary
# k2 - right boundary
def mutate(pop, sentence_set, prob):
    '''
    Each chromosome has a change to randomly mutate. A mutation can either
    be: (1) a change of sentence index, (2) a change of k1 boundary or
    (3) a change of k2 boundary.
    Returns the mutated population.
    '''

    for chromosome in pop:
        chance = random.uniform(0, 1)
        if chance <= prob:
            r = random.uniform(0, 1)
            if r < 0.33:  # change index of sentence
                index = random.randint(0, len(pop))
                if chromosome[2] >= sentence_set[index] or chromosome[3] >= sentence_set[index]:
                    diff = chromosome[3] - chromosome[2]
                    chromosome[3] = len(sentence_set[index]) - 1
                    chromosome[2] = chromosome[3] - diff
                chromosome[1] = index
            elif 0.33 <= r <= 0.66:  # change k1 boundary
                rj = random.uniform(0, 1)
                if rj <= 0.5 and chromosome[2] > 1:
                    chromosome[2] -= 1
                elif rj > 0.5 and chromosome[3] - chromosome[2] > 0:
                    chromosome[2] += 1
            elif r > 0.66:  # change k2 boundary
                rj = random.uniform(0, 1)
                if rj <= 0.5 and chromosome[3] < len(sentence_set[chromosome[1]]) - 1:
                    chromosome[3] += 1
                elif rj > 0.5 and chromosome[3] - chromosome[2] > 0:
                    chromosome[3] -= 1

    return pop


def evaluate_pop(pop, query, sentence_set, Pl, Pr):
    '''Returns the population after assigning a fitness to each chromosome.'''

    return [fitness(chromosome, query, sentence_set, Pl, Pr) for chromosome in pop]


def choose_one(fitsum):
    pos = random.uniform(0, fitsum[-1])
    for i in range(len(fitsum)):
        if pos <= fitsum[i]:
            return i
    return 0


def select_pop(pop, pop_size):
    '''
    Uses Roulette Wheel selection to create a new population of size pop_size.
    Returns the new population.
    '''
    
    new_pop = list()
    fitsum = list()
    collective_fitness = [chromosome[0] for chromosome in pop]

    fitsum.append(collective_fitness[0])
    for i in range(1, len(collective_fitness)):
        fitsum.append(collective_fitness[i - 1] + collective_fitness[i])

    already_selected = list()

    for _ in range(pop_size):
        candidate = choose_one(fitsum)
        if candidate not in already_selected:
            new_pop.append(pop[candidate])
            already_selected.append(candidate)

    return new_pop


def ga(generations, query, sentence_set, stop_words, mutation_prob, crossover_prob, Pl, Pr):
    pop = create_initial_pop(query, sentence_set, stop_words)
    pop_size = len(pop)

    for _ in range(generations):
        pop = crossover(pop, crossover_prob, query, sentence_set, Pl, Pr)
        pop = mutate(pop, sentence_set, mutation_prob)
        pop = evaluate_pop(pop, query, sentence_set, Pl, Pr)
        pop = select_pop(pop, pop_size)

    return max(pop)