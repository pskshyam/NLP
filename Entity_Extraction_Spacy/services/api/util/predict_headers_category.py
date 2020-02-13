import numpy as np
import pandas as pd
import re
import pickle
from collections import defaultdict
from itertools import chain
import nltk, string
from nltk.stem import WordNetLemmatizer
from nltk.util import ngrams

#nltk.download('punkt') # if necessary...
wordnet_lemmatizer = WordNetLemmatizer()
remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
use_ngrams = True

def lemm_tokens(tokens):
    return [wordnet_lemmatizer.lemmatize(item) for item in tokens]

def add_ngrams(list_of_words,ngrams_ind=[1,2,3]):
    tmp_list = []
    for grm in ngrams_ind:
        tmp_list.extend(list(ngrams(list_of_words, grm)))
    return [" ".join(tmp_list_i) for tmp_list_i in tmp_list]

def normalize(text):
    '''remove punctuation, lowercase, stem'''
    text = re.sub(r"[^a-zA-Z0-9]+", ' ', text)
    text = ''.join([i for i in text if not i.isdigit()])

    return lemm_tokens(nltk.word_tokenize(text.strip().lower().translate(remove_punctuation_map)))
def load_multiclass_model():
    with open("services/api/util/models/Multiclass_classifier/content_type_model_DownSamp.pkl", "rb") as f:
        cls = pickle.load(f)
    return cls

def predict_headers_category(headers):
    legend = {0:'o', 1:'t', 2:'p',  3:'w', 4:'i'}
    data_normalized = [" ".join(normalize(x)) for x in headers['content']]
    df_to_pred = pd.DataFrame(data_normalized, columns = ["content"])
    model = load_multiclass_model()
    preds = model.predict(df_to_pred)
    df =pd.DataFrame(zip(headers['content'] ,[legend[pred] for pred in preds.tolist()]) ,columns=['content', 'prediction'])
    return df
