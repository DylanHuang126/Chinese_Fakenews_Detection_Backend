import jieba
import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models import word2vec
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from keras_radam import RAdam
import tensorflow.keras.layers as L
import tensorflow as tf
from keras.models import model_from_json
import os
from keras.models import load_model
import random
import re

UTIL_PATH = 'utils/'

class Algorithm_content():
    def __init__(self, content):
        self.content = content

    def doc2vec(self, content):
        jieba.load_userdict(UTIL_PATH + 'dict.txt.big')
        temp_lst = jieba.cut(content)
        temp_str = ""
        for word in temp_lst:
            temp_str += word
            temp_str += " "
        doc = word_tokenize(temp_str.lower())
        doc_model = Doc2Vec.load(UTIL_PATH + 'd2v.model')
        self.doc_vec = doc_model.infer_vector(doc)

    def model(self):
        # preprocessing
        self.doc2vec(self.content)
        self.feat = np.array(self.doc_vec.reshape(1, 300))
        # load json and create model
        json_file = open(UTIL_PATH + 'model_onlycontent.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        loaded_model = tf.keras.models.model_from_json(loaded_model_json)
        # load weights into new model
        loaded_model.load_weights(UTIL_PATH + "model_onlycontent.h5")
        print('Successfully loaded model.')
        pred = loaded_model.predict(self.feat)
        self.pred = pred
