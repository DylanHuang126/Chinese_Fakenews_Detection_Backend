from snownlp import SnowNLP

class Sentiment():
    def __init__(self, pushs):
        self.pushs = pushs

    def label_sentiment(self):
        senti = [SnowNLP(s).sentiments if len(s) > 0 else 0.5 for s in self.pushs]
        s1 = s2 = s3 = s4 = 0
        for s in senti:
            if s >= 0 and s < 0.25:
                s1 += 1
            elif s >= 0.25 and s < 0.5:
                s2 += 1
            elif s >= 0.5 and s < 0.75:
                s3 += 1
            else:
                s4 += 1
        sep = '{} {} {} {}'.format(s1, s2, s3, s4)
        return sep