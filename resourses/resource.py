from flask_restful import Resource, reqparse, fields, marshal_with
from models import News, User, Media
from .Algorithm import NewsClassifier
from .QueryArticle import QueryArticle
from .WordCloud import WordCloud
from .sentiment import Sentiment
from .ContentOnly import Algorithm_content
import requests
from bs4 import BeautifulSoup
import pickle

news_fields = {
    'aid': fields.String,
    'title': fields.String,
    'ip': fields.String,
    'uid': fields.String,
    'msg_b': fields.String,
    'msg_n': fields.String,
    'msg_p': fields.String,
    'msg_a': fields.String,
    'content': fields.String,
    'source': fields.String,
    'time': fields.String,
    'pred': fields.String,
    'wc': fields.String,
    'sep': fields.List(fields.String),
    'postNB': fields.String,
}

search_fields = {
    'aid': fields.String,
    'title': fields.String,
    'ip': fields.String,
    'uid': fields.String,
    'msg_b': fields.String,
    'msg_n': fields.String,
    'msg_p': fields.String,
    'msg_a': fields.String,
    'content': fields.String,
    'source': fields.String,
    'PostTime': fields.String,
    'prediction': fields.String,
    'searchCount': fields.String,
    'wc': fields.String,
    'sep': fields.List(fields.String),
    'postNB': fields.String,
}

search_list_fields = {
    fields.Nested(search_fields),
}

user_fields = {
    'news': fields.List(fields.String),
    'uid': fields.String,
    'FakeNewsNB': fields.String,
}

user_list_fields = {
    fields.Nested(user_fields),
}

stat_fields = {
    'name': fields.String,
    'fakeNewsNB': fields.String
}

stat_list_fields = {
    fields.Nested(stat_fields),
}


class NewsResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument('title', type=str, required=True)
        self.parser.add_argument('source', type=str, required=False)
        self.parser.add_argument('content', type=str, required=False)
        self.args = self.parser.parse_args()
        self.c = NewsClassifier()

    #@marshal_with(news_fields, envelope='resource')
    def post(self):
        op = dict()
        q = QueryArticle()
        isFound = q.GetAid(self.args['title'])
        if isFound:
            isNew = q.CrawlArticleInfo()
            if isNew:
                #predict credibility
                content = q.df['content'][0]
                pushes = q.push
                self.c.model(content, pushes)

                #word cloud
                w = WordCloud(pushes)
                w.PushsToDoc()
                base64_img = w.drawWordCloud()

                #sentiment
                s = Sentiment(pushes)
                sep = s.label_sentiment()

                op = q.GetOutput()
                isFake = self.c.pred[0][0] >= 0.5
                # isFake = True
                op['pred'] = "{:.2%}".format(self.c.pred[0][0])[:-1]
                op['wc'] = base64_img
                op['sep'] = list(map(str, sep.split()))
                if len(op['source']) == 0:
                    source = op['source'] = self.args['source']
                else:
                    source = op['source']
                u = User.query.filter_by(uid=op['uid']).first()
                if u:
                    news = News(op['aid'], op['title'], op['uid'], op['ip'], op['msg_b'], op['msg_n'],
                                op['msg_p'], op['msg_a'], op['content'], op['source'], op['time'], op['pred'], op['wc'], sep, u)
                    news.AddNews()

                else:
                    # user legal post
                    user = op['uid'].split()[0]
                    searchlink = 'https://www.pttweb.cc/user/' + user
                    resp = requests.get(searchlink)
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    div = soup.find('div', {'class': 'mt-4 headline e7-block-title pl-3'})
                    s = div.contents[0]
                    postNB = s[s.find('共') + 2:s.find('篇') - 1]
                    op['postNB'] = postNB

                    u = User(op['uid'], op['title'], postNB, False)
                    u.AddUser()
                    news = News(op['aid'], op['title'], op['uid'], op['ip'], op['msg_b'], op['msg_n'],
                                op['msg_p'], op['msg_a'], op['content'], op['source'], op['time'], op['pred'], op['wc'], sep, u)
                    news.AddNews()

                if isFake:
                    s = Media.query.filter_by(MediaName=source).first()
                    if s:
                        s.AddFakeNews()
                    else:
                        s = Media(source)
                        s.AddMedia()
            else:
                op = q.GetDataBase()

        else:
            c = Algorithm_content(self.args['content'])
            c.model()
            op['pred'] = "{:.2%}".format(c.pred[0][0])[:-1]
            op['title'] = self.args['title']
            op['content'] = self.args['content']

        return op

class HotSearchResource(Resource):
    def __init__(self):
        self.parser = reqparse.RequestParser(bundle_errors=True)
        self.parser.add_argument('aid', type=str, required=True)
        self.args = self.parser.parse_args()

    @marshal_with(search_fields, envelope='resource')
    def post(self):
        op = dict()
        n = News.query.filter_by(aid=self.args['aid']).first()
        if n:
            op = {'aid': n.aid, 'title': n.title, 'uid': n.uid, 'ip': n.ip,
                   'msg_b': str(n.msg_b), 'msg_n': str(n.msg_n), 'msg_p': str(n.msg_p), 'msg_a': str(n.msg_a),
                   'content': n.content, 'source': n.source, 'PostTime': n.PostTime, 'QueryTime': str(n.QueryTime),
                   'prediction': str(n.prediction), 'searchCount': str(n.SearchCount), 'wc': n.base64_img,
                   'sep': list(map(str, n.sentiment.split())), 'postNB': n.poster.PostNB}
            n.AddNB()
        return op
        # 回傳新聞資訊

class HotSearchAllResource(Resource):
    #@marshal_with(search_list_fields, envelope='resource')
    def get(self):
        op = []
        news = News.query.order_by(News.SearchCount).all()
        if news:
            op = [{'aid': n.aid, 'title': n.title, 'uid': n.uid, 'ip': n.ip,
                   'msg_b': str(n.msg_b), 'msg_n': str(n.msg_n), 'msg_p': str(n.msg_p), 'msg_a': str(n.msg_a),
                   'content': n.content, 'source': n.source, 'PostTime': n.PostTime, 'QueryTime': str(n.QueryTime),
                   'prediction': str(n.prediction), 'searchCount': str(n.SearchCount)} for n in news]
        return op
        # 回傳所有資訊json

class SuspectUserResource(Resource):
    #@marshal_with(user_list_fields, envelope='resource')
    def get(self):
        op = []
        userList = User.query.filter_by(isFake = True)
        if userList:
            op = []
            for u in userList:
                t = u.title.split('%&%')
                try:
                    t.remove("")
                except:
                    pass
                op.append({'uid': u.uid, 'postNB': u.PostNB, 'title': t})
        return op
        #回傳所有使用者以及他所有的文章代碼

class StatResource(Resource):
    #@marshal_with(stat_list_fields, envelope='resource')
    def get(self):
        op = []
        mediaList = Media.query.order_by(Media.FakeNewsNB).limit(5).all()
        if mediaList:
            op = [{'name': m.MediaName, 'fakeNewsNB': m.FakeNewsNB} for m in mediaList]
        return op

class LoadResource(Resource):
    def get(self):
        with open('utils/fake_news_db.pkl', 'rb') as infile:
            n = pickle.load(infile)
        for i in range(n[0].shape[0]):
            if '討論' not in n[1][i] and '問卦' not in n[1][i]:
                u = User(n[0][i], n[1][i], n[2][i], True)
                u.AddUser()
        return 'finish'