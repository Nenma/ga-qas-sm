import requests
import json
import re
from nltk.corpus import stopwords

import query_analyzer as qa
import data_prep as dp
import answer_extraction as ae


def get_raw_snippets(query, counter):
    '''
    Calls Google's Custom Search API to search for snippets to the query
    and writes them to a file.
    '''

    keys_json = open('config/keys.json', 'r').read()
    keys = json.loads(keys_json)
    cx_key = keys['cx_key']
    api_key = keys['api_key']

    response = requests.get(
        'https://customsearch.googleapis.com/customsearch/v1',
        params={'cx': cx_key,
                'lr': 'lang_en',
                'num': counter,
                'q': query,
                'key': api_key}
    )

    test = open('data/raw_snippets.txt', 'w')
    json_response = response.json()
    for i in range(counter):
        snipp = json_response['items'][i]['snippet']
        if snipp:
            snipp = snipp.strip('\n')
            snipp = snipp.replace('\n', '')
            test.write(snipp + '\n')


def read_snippets():
    test = open('data/raw_snippets.txt', 'r')
    snippets = test.readlines()

    # normalize snippets (~)
    snippets = [snipp.strip().upper().encode('ascii', 'ignore').decode() for snipp in snippets]

    # get rid of parantheses, also get rid of commas (with the intention of avoiding appositions)
    # e.g.: the author, born in 1985, wrote the book
    snippets = [re.sub('[\(\)\[\],]', '', snipp) for snipp in snippets]

    # transform intervals of time NUMBER1-NUMBER2 into NUMBER1 TO NUMBER2
    for i, snipp in enumerate(snippets):
        interval_pairs = re.findall(r'([0-9]+)(-[0-9]+)+', snipp)
        for pair in interval_pairs:
            interval = pair[0] + pair[1]
            snipp = re.sub(interval, pair[0] + ' TO ' + pair[1][1:], snipp)
        snippets[i] = snipp

    return snippets


def process_answer(chromosome, sentence_set):
    '''
    Cancatenate the words of the asnwer candidate into a single string.
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


def select_elite(pop, query, unigrams, stop_words):
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
        
        if any([unigram[0] in ans.split() and unigram[1] > min_quality for unigram in unigrams]) and \
            not any([stop_word.upper() in ans.split() for stop_word in stop_words]) and \
            not any([query_word in ans.split() for query_word in query]) and \
            ans not in elite:
                elite.append(chromosome)

    return elite


if __name__ == '__main__':
    query = 'who wrote harry potter'
    counter = 10  # number of snippets to be retrieved (max. 10)
    stop_words = set(stopwords.words('english'))

    resp = get_raw_snippets(query, counter)

    print('Query:', query)
    eat = qa.get_EAT(query)

    snippets = read_snippets()
    sentence_set = dp.get_sentence_set(snippets, stop_words)
    unigrams = dp.get_unigrams(sentence_set, stop_words)
    sents, answs = ae.use_qa_store(eat, [unigram[0] for unigram in unigrams])
    max_sent_len = max([len(sent.split()) for sent in sentence_set])
    pl, pr = ae.calc_syn_contribution(sents, answs, max_sent_len)

    normal_query = dp.normalize_query(query)

    candidates = list()
    for _ in range(20):
        pop = ae.ga(20, normal_query, sentence_set, stop_words, 0.1, 0.7, pl, pr)
        for candidate in pop:
            candidates.append(candidate)

    elite = select_elite(candidates, normal_query, unigrams, stop_words)
    if len(elite) > 0:
        best = max(elite)
        print('Sentence:', sentence_set[best[1]])
        ans = process_answer(best, sentence_set)
        print('Answer:', ans)
        ae.add_to_qa_store(eat, query.upper(), sentence_set[best[1]], ans)
    else:
        print('Not enough data available...')
