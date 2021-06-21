'''
Module containing the genetic algorithm used for answer extraction.
'''

import random


def create_initial_pop(sentence_set, stop_words):
    '''
    Initializes the population with a number of chromosomes equal to the
    size of the sentence set. A chromosome is a list [K, s, k1, k2] where
    K is the initial fitness (0), s is the sentence index, and k1 and k2 
    are the boundaries of the n-gram in the sentence.
    Returns the list of chromosomes.
    '''
    pop = list()
    for i, sentence in enumerate(sentence_set):
        sentence = sentence.split()
        # generate new k1 and k2 if the n-gram contains stopwords
        bad_candidate = True
        while bad_candidate:
            bad_candidate = False
            k1 = random.randint(0, len(sentence) - 1)
            k2 = random.randint(k1, len(sentence) - 1)
            if any([word in sentence[k1:k2] for word in stop_words]):
                bad_candidate = True
        
        pop.append([0, i, k1, k2])

    return pop


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
        if word in Pl:
            part_sum += query_weight(word, query) * Pl[word][i - 1]
    
    # words after the answer candidate:
    for i in range(k2 + 1, len(sentence)):
        word = sentence[i]
        if word in Pr:
            part_sum += query_weight(word, query) * Pr[word][i - k2 - 1]

    chromosome[0] = part_sum

    return chromosome


# a chromosome is [K, s, k1, k2] where
# K - fitness of answer candidate
# s - sentence index
# k1 - left boundary
# k2 - right boundary
def crossover(pop, pop_size, prob, query, sentence_set, Pl, Pr):
    '''
    Randomly select 2 chromosomes and create 2 children whose
    k1 and k2 boundaries are a mix of the 2 parents'. Do this
    pop_size times.
    Returns the new population.
    '''
    new_pop = pop[:]
    for _ in range(len(pop)):
        chance = random.uniform(0, 1)
        if chance <= prob:
            first_parent = random.randint(0, pop_size - 1)
            second_parent = random.randint(0, pop_size - 1)
            while second_parent == first_parent:
                second_parent = random.randint(0, pop_size - 1)

            first_parent = pop[first_parent]
            first_index = first_parent[1]
            first_sentence = sentence_set[first_index].split()
            first_k1 = first_parent[2]
            first_k2 = first_parent[3]

            second_parent = pop[second_parent]
            second_index = second_parent[1]
            second_sentence = sentence_set[second_index].split()
            second_k1 = second_parent[2]
            second_k2 = second_parent[3]

            b1 = min(first_k1, second_k1)
            b2 = min(max(first_k2, second_k2), len(first_sentence))
            b3 = max(first_k1, second_k1)
            b4 = min(max(first_k2, second_k2), b3)

            if 0 <= b1 <= b2 <= len(first_sentence) - 1:
                first_child = [0, first_index, b1, b2]
                first_child[0] = fitness(first_child, query, sentence_set, Pl, Pr)
                new_pop.append(first_child)

            if 0 <= b3 <= b4 <= len(second_sentence) - 1:
                second_child = [0, second_index, b3, b4]
                second_child[0] = fitness(second_child, query, sentence_set, Pl, Pr)
                new_pop.append(second_child)

    return new_pop


# a chromosome is [K, s, k1, k2] where
# K - fitness of answer candidate
# s - sentence index
# k1 - left boundary
# k2 - right boundary
def mutate(pop, pop_size, sentence_set, prob):
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
            # change index of sentence
            if r < 0.33:
                index = random.randint(0, pop_size - 1)
                sentence = sentence_set[index].split()
                sen_len = len(sentence) - 1
                diff = chromosome[3] - chromosome[2]

                # (k1 <= k2 < 0 < sen_len) OR (k1 < 0 <= k2 <= sen_len)
                if ((chromosome[2] < 0 and chromosome[3] < 0) or (chromosome[2] < 0 and 0 <= chromosome[3] <= sen_len)):
                    chromosome[2] = 0
                    if diff <= sen_len:
                        chromosome[3] = chromosome[2] + diff
                    else:
                        chromosome[3] = sen_len
                # (0 < sen_len < k1 <= k2) OR (0 <= k1 <= sen_len < k2)
                elif ((chromosome[2] > sen_len and chromosome[3] > sen_len) or (0 <= chromosome[2] <= sen_len and 0 <= chromosome[3] > sen_len)):
                    chromosome[3] = sen_len
                    if diff <= sen_len:
                        chromosome[2] = chromosome[3] - diff
                    else:
                        chromosome[2] = 0
            # change k1 boundary
            elif 0.33 <= r <= 0.66:
                rj = random.uniform(0, 1)
                if rj <= 0.5 and chromosome[2] > 1:
                    chromosome[2] -= 1
                elif rj > 0.5 and chromosome[3] - chromosome[2] > 0:
                    chromosome[2] += 1
            # change k2 boundary
            elif r > 0.66:
                rj = random.uniform(0, 1)
                if rj <= 0.5 and chromosome[3] < len(sentence_set[chromosome[1]].split()) - 1:
                    chromosome[3] += 1
                elif rj > 0.5 and chromosome[3] - chromosome[2] > 0:
                    chromosome[3] -= 1

    return pop


def evaluate_pop(pop, query, sentence_set, Pl, Pr):
    '''Returns the population after assigning a fitness to each chromosome.'''

    return [fitness(chromosome, query, sentence_set, Pl, Pr) for chromosome in pop]


def pick_one(collective_fitness):
    maxi = sum(collective_fitness)
    pick = random.uniform(0, maxi)
    current = 0
    for i in range(len(collective_fitness)):
        current += collective_fitness[i]
        if current > pick:
            return i
    return 0


def select_pop(pop, pop_size):
    '''
    Uses Roulette Wheel selection to create a new population of size pop_size.
    Returns the new population.
    '''
    
    new_pop = list()
    collective_fitness = [chromosome[0] for chromosome in pop]

    already_selected = list()

    for _ in range(pop_size):
        candidate = pick_one(collective_fitness)
        if candidate not in already_selected:
            new_pop.append(pop[candidate])
            already_selected.append(candidate)
        else:
            already_selected_flag = True
            while already_selected_flag:
                candidate = random.randint(0, len(pop) - 1)
                if candidate not in already_selected:
                    already_selected_flag = False
                    new_pop.append(pop[candidate])
                    already_selected.append(candidate)
    return new_pop


def ga(generations, query, sentence_set, stop_words, mutation_prob, crossover_prob, Pl, Pr):
    pop = create_initial_pop(sentence_set, stop_words)
    pop_size = len(pop)

    for i in range(generations):
        # print('Training generation', i + 1, '...')
        pop = crossover(pop, pop_size, crossover_prob, query, sentence_set, Pl, Pr)
        pop = mutate(pop, pop_size, sentence_set, mutation_prob)
        pop = evaluate_pop(pop, query, sentence_set, Pl, Pr)
        pop = select_pop(pop, pop_size)
        # print('Finished generation', i + 1)

    return pop