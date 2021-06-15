'''Main module.'''

import re
from nltk.corpus import stopwords

import spacy
from profanity_filter import ProfanityFilter

import crawler.google_crawler as gc
import crawler.twitter_crawler as tc

import util.qa_store_util as qasu
import util.tw_store_util as twsu

import query_analyzer as qa
import data_prep as dp
import answer_extraction as ae


STOP_WORDS = set(stopwords.words('english'))
GENERATIONS = 20
ITERATIONS = 20
MUTATION_PROB = 0.1
CROSSOVER_PROB = 0.7

nlp = spacy.load('en_core_web_sm')
pf = ProfanityFilter(nlps={'en': nlp})
nlp.add_pipe(pf.spacy_component, last=True)


def read_data():
    test = open('data/raw_data.txt', 'r')
    data = test.readlines()
    test.close()

    return data


def process_answer(chromosome, sentence_set):
    '''
    Cancatenate the words of the answer candidate into a single string.
    Returns the string.
    '''

    sentence = sentence_set[chromosome[1]]
    sentence = sentence.split()

    answer = ''
    if chromosome[2] == chromosome[3]:
        answer = sentence[chromosome[2]]
    else:
        for i in range(chromosome[2], chromosome[3]):
            answer += sentence[i] + ' '

    return answer


def select_elite(pop, query, sentence_set, unigrams, stop_words):
    '''
    Reduce the chromosomes of the population to only unique ones,
    after which only keep those whose answer candidate does not
    contain stopwords or query terms.
    Returns the filtered chromosomes.
    '''
    
    unique_chromosomes = list()
    for chromosome in pop:
        if chromosome in unique_chromosomes:
            continue
        else:
            unique_chromosomes.append(chromosome)

    elite = list()
    min_quality = 3
    for chromosome in unique_chromosomes:
        ans = process_answer(chromosome, sentence_set)
        sent = sentence_set[chromosome[1]].rstrip().strip()
        
        # not any([stop_word.upper() in ans.split() for stop_word in stop_words]) and \
        if any([unigram[0] in ans.split() and unigram[1] > min_quality for unigram in unigrams]) and \
            any([query_word in ans.split() for query_word in query]) and \
            not nlp(sent)._.is_profane and \
            ans not in elite:
                elite.append(chromosome)

    return elite


if __name__ == '__main__':
    query = 'Portugal'

    # gc.get_raw_snippets(query, 10)
    tc.get_raw_posts(query, 20)

    print('Query:', query)
    # eat = qa.get_EAT(query)

    data = read_data()

    sentence_set = dp.get_sentence_set(data, STOP_WORDS)
    unigrams = dp.get_unigrams(sentence_set, STOP_WORDS)
    unigram_words = [unigram[0] for unigram in unigrams]

    # sents, answs = qasu.use_qa_store(eat, unigram_words)
    sents, answs = twsu.use_tw_store(unigram_words)

    max_sent_len = max([len(sent.split()) for sent in sentence_set])
    pl, pr = ae.calc_syn_contribution(sents, answs, max_sent_len)

    normal_query = dp.normalize_query(query)

    candidates = list()
    for _ in range(ITERATIONS):
        pop = ae.ga(GENERATIONS, normal_query, sentence_set, STOP_WORDS, MUTATION_PROB, CROSSOVER_PROB, pl, pr)
        for candidate in pop:
            candidates.append(candidate)

    elite = select_elite(candidates, normal_query, sentence_set, unigrams, STOP_WORDS)
    if len(elite) > 0:
        best = max(elite)
        sentence = sentence_set[best[1]].rstrip().strip()
        print('Sentence:', sentence)
        ans = process_answer(best, sentence_set)
        print('Answer:', ans)

        # qasu.add_to_qa_store(eat, query.upper(), sentence_set[best[1]], ans)
        twsu.add_to_tw_store(sentence, query.upper())
    else:
        print('Not enough data available...')
