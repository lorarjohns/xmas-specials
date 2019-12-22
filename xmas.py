import pandas as pd 
import json
import re

import gensim 
import gensim.corpora as corpora
from gensim.utils import simple_preprocess
from gensim.models import TfidfModel, CoherenceModel

from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize

stop_words = stopwords.words('english')
stop_words.extend(['from'])

def preprocess_text(doc):
    #newlines = re.compile(r'\n')
    #doc = re.sub(newlines, r' ', doc)
    for sent in doc:
        yield(simple_preprocess(str(sent), deacc=True))

with open('articles.json', 'r') as infile:
    data = json.load(infile)

movies = pd.DataFrame(data).drop('related', axis=1)
print(movies.head())

'''Get the data in a format gensim can parse'''
docs = movies.contents.values.tolist()
words = [preprocess_text(doc) for doc in ', '.join([doc for doc in docs])]

'''create ngram models and transform them for speed'''
bigrams = gensim.models.Phrases(words, min_count=5)
trigrams = gensim.models.Phrases(bigrams[words])

bigram_mod = gensim.models.phrases.Phraser(bigrams)
trigram_mod = gensim.models.phrases.Phraser(trigrams)

print(words)
#print(trigram_mod[bigram_mod[words[10]]])
