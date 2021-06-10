import pandas as pd


def use_qa_store(eat_type):
    '''Acces the qa_store.csv to get the (sentences, aswers) pairs for a certain EAT.'''

    store = pd.read_csv('qa_store.csv', header=1, encoding='utf8', names=['type', 'question', 'sentence', 'answer'])
    person_store = store[store['type'] == eat_type]
    
    sentences = person_store['sentence'].to_list()
    answers = person_store['answer'].to_list()

    return sentences, answers


def calc_syn_contribution(sentences, answers):
    for i in range(len(sentences)):
        sentences[i] = sentences[i].replace(answers[i], 'w')
    
    # use regex to calculate the frequency values
    # FIRST_WORD\W+(\w+\W+){n}SECOND_WORD - regex for matching two words within exactly n words of each other