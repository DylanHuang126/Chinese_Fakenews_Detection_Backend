import requests
from bs4 import BeautifulSoup
from utils.PttWebCrawler.crawler import *
import json
import pandas as pd
from shared import db
from models import News
import datetime


class QueryArticle():
    def __init__(self):
        self.title = ''
        self.aid = ''
        self.df = None
        self.postIP = ''
        self.postUid = ''
        self.msg_b = self.msg_n = self.msg_p = self.msg_a = 0
        self.push = ''
        self.content = ''
        self.source = ''
        self.time = None

    # 取得文章代碼，沒找到return空字串
    def GetAid(self, title):
        gossipSearchLink = "https://www.ptt.cc/bbs/Gossiping/search?q="
        # q = title[3:len(title) - 5]
        q = title[:10]
        resp = requests.get(gossipSearchLink + q, cookies={'over18': '1'})
        soup = BeautifulSoup(resp.text, 'html.parser')
        url = ''
        for result in soup.findAll("div", {"class": "title"}):
            if "Re:" not in result.findAll("a")[0].contents[0] and '[新聞]' in result.findAll("a")[0].contents[0]:
                url = result.findAll("a")[0]['href']
                break
        while url == '':
            pre = False
            for a in soup.findAll("a", {"class": "btn wide"}):
                if a.contents[0] == '‹ 上頁':
                    pre = True
                    u = 'https://www.ptt.cc' + a['href']
                    resp = requests.get(u, cookies={'over18': '1'})
                    soup = BeautifulSoup(resp.text, 'html.parser')
                    for result in soup.findAll("div", {"class": "title"}):
                        if "Re:" not in result.findAll("a")[0].contents[0] and '[新聞]' in \
                                result.findAll("a")[0].contents[0]:
                            url = result.findAll("a")[0]['href']
                            break
                    if url:
                        break
            if not pre or url:
                break
        if url:
            self.aid = url[url.find("M"):url.rfind(".")]
            return True
        return False

    # 使用ptt-web-crawler爬文章完整資訊
    def CrawlArticleInfo(self):
        exist = News.query.filter_by(aid = self.aid).first()
        if exist:
            return False
        else:
            c = PttWebCrawler(as_lib=True)
            c.parse_article(self.aid, 'Gossiping')
            ## json format: Gossiping-"aid".json
            JsonFile = "Gossiping-{}.json".format(self.aid)

            with open(JsonFile) as infile:
                data = json.load(infile)
            self.df = pd.io.json.json_normalize(data)
            self.parsePushes()
            return True

    def MessageCount(self):
        self.msg_b = self.df['message_count.boo'][0]
        self.msg_n = self.df['message_count.neutral'][0]
        self.msg_p = self.df['message_count.push'][0]
        self.msg_a = self.df['message_count.all'][0]

    def UserInfo(self):
        self.postUid = self.df['author'][0]
        self.postIP = self.df['ip'][0]

    def NewsInfo(self):
        time = datetime.datetime.strptime(self.df['date'][0], '%c').strftime("%Y年%m月%d日 %H:%M")
        self.time = time
        self.title = self.df['article_title'][0][5:]
        content = self.df['content'][0]
        if content.find("完整新聞內文") != -1:
            for j in range(content.find("完整新聞內文") + 8, len(content)):
                if content[j] == "5" and content[j + 1] == ".":
                    break
                self.content += content[j]
        else:
            self.content = content

        if content.find("媒體來源") != -1:
            temp_source = ''
            for j in range(7, len(content)):
                if j > 7 and content[j] == " ":
                    break
                temp_source += content[j]
            temp_source = temp_source.lower()
            if "蘋果" in temp_source or "apple" in temp_source:
                self.source = "蘋果"
            elif "自由" in temp_source:
                self.source = "自由"
            elif "聯合" in temp_source or "udn" in temp_source:
                self.source = "聯合"
            elif "風傳媒" in temp_source:
                self.source = "風傳媒"
            elif "東森" in temp_source or "ettoday" in temp_source:
                self.source = "東森"
            elif "奇摩" in temp_source or "yahoo" in temp_source:
                self.source = "奇摩"
            elif "壹週刊" in temp_source:
                self.source = "壹週刊"
            elif "中時" in temp_source:
                self.source = "中時"
            elif "tvbs" in temp_source:
                self.source = "TVBS"
            elif "上報" in temp_source:
                self.source = "上報"
            elif temp_source == '':
                self.source = "其他"


    def parsePushes(self):
        push_before = self.df['messages'][0]
        push_after = []
        for i in range(len(push_before)):
            push_after.append(push_before[i]['push_content'])
        self.push = push_after

    def GetOutput(self):
        self.MessageCount()
        self.UserInfo()
        self.NewsInfo()

        op = {'aid': self.aid, 'title': self.title, 'ip' : str(self.postIP), 'uid' : str(self.postUid),
              'msg_b' : str(self.msg_b), 'msg_n': str(self.msg_n), 'msg_p' : str(self.msg_p), 'msg_a' : str(self.msg_a),
              'content' : self.content, 'source' : self.source, 'time' : self.time}
        return op

    def GetDataBase(self):
        news = News.query.filter_by(aid=self.aid).first()
        news.AddNB()
        op = {'aid': news.aid, 'title': news.title, 'ip': str(news.ip), 'uid': str(news.uid),
              'msg_b': str(news.msg_b),'msg_n': str(news.msg_n), 'msg_p': str(news.msg_p), 'msg_a': str(news.msg_a),
              'content': news.content, 'source': news.source, 'time': news.PostTime, 'pred': str(news.prediction), 'wc': news.base64_img,
              'sep': list(map(str,news.sentiment.split())), 'postNB': news.poster.PostNB}

        return op
