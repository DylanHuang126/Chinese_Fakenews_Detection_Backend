import os
import random
import re

from gensim.models.doc2vec import Doc2Vec, TaggedDocument
from gensim.models import word2vec
from keras.models import load_model, model_from_json
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
import jieba
import numpy as np
import tensorflow as tf
import tensorflow.keras.layers as L


UTIL_PATH = 'utils/'
jieba.load_userdict(UTIL_PATH + 'dict.txt.big')

class NewsClassifier():

    def __init__(self):
        self.doc_model = Doc2Vec.load(UTIL_PATH + 'd2v.model')
        self.stopword_set = set()

        with open(UTIL_PATH + 'stopwords.txt', 'r', encoding='utf-8') as stopwords:
            for stopword in stopwords:
                self.stopword_set.add(stopword.strip('\n'))
        self.vectorizer = TfidfVectorizer(max_features=20)
        self.comment_model = word2vec.Word2Vec.load(UTIL_PATH + "ptt_model_v2.bin")

        # load json and create model
        with open(UTIL_PATH + 'model+kuo.json', 'r') as json_file:
            loaded_model_json = json_file.read()
        self.classifier = tf.keras.models.model_from_json(loaded_model_json)

        # load weights into new model
        self.classifier.load_weights(UTIL_PATH + "model+kuo.h5")
        print('Successfully loaded model.')

    def doc2vec(self, content):
        temp_lst = jieba.cut(content)
        temp_str = ' '.join(temp_lst)
        doc = word_tokenize(temp_str.lower())

        return self.doc_model.infer_vector(doc)

    def get_pushes_keyword(self, pushes):
        pushes_seg = []
        for push in pushes:
            seg = ''
            words = jieba.cut(push, cut_all=False)
            for word in words:
                if word not in self.stopword_set:
                    word = re.sub("\d+", "", word)
                    if word:
                        seg += word + ' '
            pushes_seg.append(seg)
        if pushes_seg:
            wt = self.vectorizer.fit_transform(pushes_seg).toarray()
            word = self.vectorizer.get_feature_names()
            return wt, word
        else:
            return None, None

    def comment2vec(self, pushes):
        vac = self.comment_model.wv
        wt, words = self.get_pushes_keyword(pushes)
        vecs = dict()
        if words is not None:
            for idx, word in enumerate(words):
                try:
                    vecs[idx] = vac[word]
                except:
                    vecs[idx] = np.zeros(250)
            return np.array([kw for _, kw in vecs.items()]).reshape(-1)

        return np.zeros(5000) # if no keywords

    def model(self, content, pushes):
        doc = self.doc2vec(content)
        cmt = self.comment2vec(pushes)
        feat = np.append(doc, cmt).reshape(1, -1)

        pred = self.classifier.predict(feat)
        self.pred = pred