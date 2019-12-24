import pandas as pd 
import json
# import re
from pprint import pprint
from halo import Halo

import spacy
import gensim 
# import gensim.corpora as corpora
from gensim.corpora import Dictionary
from gensim.utils import simple_preprocess
from gensim.models import TfidfModel, CoherenceModel, LdaModel

from nltk.corpus import stopwords

import pyLDAvis

# from nltk.tokenize import sent_tokenize

stop_words = stopwords.words('english')
stop_words.extend(['from'])


def preprocess_text(words):

    # newlines = re.compile(r'\n')
    # doc = re.sub(newlines, r' ', doc)
    # for sent in doc:
    #    return simple_preprocess(str(sent), deacc=True)  
    return [[word for word in simple_preprocess(str(doc))
            if word not in stop_words] for doc in words]


def lemmatize_text(words, pos=['NOUN', 'ADJ', 'VERB', 'ADV']):
    output = []
    for sent in words:
        doc = nlp(" ".join(sent))
        output.append([token.lemma_ for token in doc if token.pos_ 
                       in pos])
    return output


with open('articles.json', 'r') as infile:
    data = json.load(infile)

movies = pd.DataFrame(data).drop('related', axis=1)
print(movies.head())

spinner = Halo(text='Making a list of documents. . .')
spinner.start()
'''Get the data in a format gensim can parse'''
docs = movies.contents.values.tolist()
# words = [preprocess_text(doc) for doc in ', '.join([doc for doc in docs])]
words = preprocess_text(docs)
spinner.succeed(text=f"Ho ho ho! Preprocessed {len(docs)} texts!")

'''create ngram models and transform them for speed'''
bigrams = gensim.models.Phrases(words)
trigrams = gensim.models.Phrases(bigrams[words])

bigram_mod = gensim.models.phrases.Phraser(bigrams)
trigram_mod = gensim.models.phrases.Phraser(trigrams)


def make_bigrams(words):
    return [bigram_mod[doc] for doc in words]


def make_trigrams(words):
    return [trigram_mod[bigram_mod[doc]] for doc in words]


spinner = Halo(text='Wrapping bigrams and trigrams . . .')
spinner.start()

bigram_words = make_bigrams(words)
# trigram_words = make_trigrams(words)

nlp = spacy.load('en_core_web_lg', disable=['parser', 'ner'])
lemma_words = lemmatize_text(bigram_words)
spinner.succeed(text='spaCy is ready to deliver your corpus to LDA!')

'''Prep data for topic model'''
spinner = Halo(text='Blei Claus is on the way. Have you been good or bad?')
spinner.start()
id2word = Dictionary(lemma_words)

texts = lemma_words

tf_corpus = [id2word.doc2bow(text) for text in texts]
# [[(id2word[id], freq) for id, freq in doc] for doc in corpus]


'''Build LDA model'''

lda = LdaModel(corpus=tf_corpus,
               id2word=id2word,
               num_topics=30,
               random_state=25,
               update_every=5,
               chunksize=100,
               passes=10,
               alpha='auto',
               eval_every=5,
               eta='auto',
               per_word_topics=True)

spinner.succeed(text='Merry xmas, your topics are here!')

pprint(lda.print_topics())
doc_lda = lda[tf_corpus]
spinner.succeed(text='Your topics are here!')

'''Evaluation metrics'''
print(f"Perplexity: {lda.log_perplexity(tf_corpus)}")
lda_coherence = CoherenceModel(model=lda,
                               texts=lemma_words,
                               dictionary=id2word,
                               coherence='c_v')
lda_coherence_score = lda_coherence.get_coherence()
print(f"Coherence: {lda_coherence_score}")

import numpy as np
'''Gridsearch'''
min_topics = 4
max_topics = 100
step_size = 2
    


vis = pyLDAvis.gensim.prepare(lda, tf_corpus, id2word)

pyLDAvis.save_html(vis, 'lda.html')