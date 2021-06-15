# Genetic Algorithm based Question Answering System for Social Media

### Reference paper: [Genetic Algorithms for syntactic and data-driven Question Answering on the Web](https://www.researchgate.net/profile/Alejandro-Figueroa-15/publication/271911238_Genetic_Algorithms_for_syntactic_and_data-driven_Question_Answering_on_the_Web/links/54d6fb680cf2970e4e6fb60b/Genetic-Algorithms-for-syntactic-and-data-driven-Question-Answering-on-the-Web.pdf)

At the moment:
- A query with an EAT (Expected Answer Type) of either a PERSON, a LOCATION or a DATE can be used as input.
- Using the entries in the *qa_store.csv* as reference and going through a QA cycle - the process of answering the query by evolutionary means using the genetic algorithm - an answer in produced.
- At the end of the QA cycle, the new **{EAT, query, context_sentence, answer}** pair is added to the *qa_store.csv*. The *context_sentence* is the sentence in which the answer was found.
- A random element from top trending on Twitter is chosen and is used to search for tweets, from which the algorithm will pick the most relevant and make a Twitter post (in a similar fashion as above)