import jieba
import wordcloud
import json
import pandas as pd
import numpy as np
import random
import matplotlib
matplotlib.use("agg")
from matplotlib import pyplot as plt
import re

from io import BytesIO
import base64

UTIL_PATH = 'utils/'

class WordCloud():
    def __init__(self, pushs):
        self.pushs = pushs
        self.docs = ''

    def PushsToDoc(self):
        stopword_set = set()
        with open(UTIL_PATH + 'stopwords.txt', 'r', encoding='utf-8') as stopwords:
            for stopword in stopwords:
                stopword_set.add(stopword.strip('\n'))
        for push in self.pushs:
            words = jieba.cut(push, cut_all=False)
            for word in words:
                if word not in stopword_set:
                    word = re.sub("\d+", "", word)
                    if word:
                        self.docs += word + ' '
        return

    # def random_color_func(self, word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=100):
    #     h = int(100.0 * float(random_state.randint(80, 220)) / 255.0)
    #     s = int(100.0 * float(random_state.randint(150, 250)) / 255.0)
    #     l = int(100.0 * float(random_state.randint(40, 220)) / 255.0)
    #     return "hsl({}, {}%, {}%)".format(h, s, l)

    def random_color_func(self, word=None, font_size=None, position=None,  orientation=None, font_path=None, random_state=100):
        hsl = [(11, 100, 99), (22, 100, 49), (34, 98, 47), (43, 99, 47), (34, 100, 50), (50, 100, 50), (46, 100, 53),
               (22, 100, 50)]
        c = random.choice(hsl)
        return "hsl({}, {}%, {}%)".format(c[0], c[1], c[2])

    # draw word cloud, return base64 img
    def drawWordCloud(self):
        FONT = UTIL_PATH + 'simhei.ttf'
        wc = wordcloud.WordCloud(font_path = FONT, random_state=None, width=800, height=400, color_func=self.random_color_func).generate(self.docs)
        plt.figure(figsize=(20,10), facecolor='k')
        plt.imshow(wc)
        plt.axis("off")
        plt.tight_layout(pad=0)
        b = BytesIO()
        plt.savefig(b, format='png')
        b.seek(0)
        base64_img = base64.b64encode(b.getvalue()).decode('utf-8')
        plt.close()
        return base64_img
