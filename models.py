import datetime
from flask_sqlalchemy import SQLAlchemy
from shared import db

class News(db.Model):
    __tablename__ = 'news'
    id = db.Column(db.Integer, primary_key = True)
    aid = db.Column(db.String(30))
    title = db.Column(db.String(100))
    uid = db.Column(db.String(40), nullable = True)
    ip = db.Column(db.String(40), nullable = True)
    msg_b = db.Column(db.Integer, nullable = True)
    msg_n = db.Column(db.Integer, nullable = True)
    msg_p = db.Column(db.Integer, nullable = True)
    msg_a = db.Column(db.Integer, nullable = True)
    content = db.Column(db.String(2000), nullable=True)
    source = db.Column(db.String(20), nullable=True)

    PostTime = db.Column(db.String(50), nullable = True)
    QueryTime = db.Column(db.DateTime, default = datetime.datetime.utcnow(), nullable = True)

    prediction = db.Column(db.String(10), nullable = True)
    SearchCount = db.Column(db.Integer, nullable = True)

    base64_img = db.Column(db.String(10000), nullable=True)
    sentiment = db.Column(db.String(30), nullable=True)

    poster_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, aid, title, uid, ip, msg_b, msg_n, msg_p, msg_a, content, source, PostTime, prediction, base64_img, sentiment, poster):
        self.aid = aid
        self.title = title
        self.uid = uid
        self.ip = ip
        self.msg_b = msg_b
        self.msg_n = msg_n
        self.msg_p = msg_p
        self.msg_a = msg_a
        self.content = content
        self.source = source
        self.PostTime = PostTime
        self.prediction = prediction
        self.SearchCount = 1
        self.base64_img = base64_img
        self.sentiment = sentiment
        self.poster = poster

    def AddNews(self):
        db.session.add(self)
        db.session.commit()

    def AddNB(self):
        self.SearchCount += 1
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<%r>' % self.title

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    uid = db.Column(db.String(40))
    PostNB = db.Column(db.Integer, nullable = True)
    title = db.Column(db.String(200))
    news = db.relationship('News', backref='poster')
    isFake = db.Column(db.Boolean, default = False)

    def __init__(self, uid, title, PostNB, isFake):
        self.uid = uid
        self.PostNB = PostNB
        self.title = title
        self.isFake = isFake

    def AddUser(self):
        db.session.add(self)
        db.session.commit()

    # def AddFakeNews(self):
    #     self.FakeNewsNB += 1
    #     db.session.add(self)
    #     db.session.commit()

    def __repr__(self):
        return '<%r>' % self.uid

class Media(db.Model):
    __tablename__ = 'media'
    id = db.Column(db.Integer, primary_key = True)
    MediaName = db.Column(db.String(10))
    FakeNewsNB = db.Column(db.Integer, default = 1)

    def __init__(self, MediaName):
        self.MediaName = MediaName

    def AddMedia(self):
        db.session.add(self)
        db.session.commit()

    def AddFakeNews(self):
        self.FakeNewsNB += 1
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        return '<%r>' % self.MediaName