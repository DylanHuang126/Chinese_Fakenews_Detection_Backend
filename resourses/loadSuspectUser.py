import pickle
from models import User

with open('utils/fake_news_db.pkl', 'rb') as infile:
    n = pickle.load(infile)

for i in range(n[0].shape[0]):
    if '討論' not in n[1][i]:
        u = User(n[0][i], n[1][i], n[2][i], True)
        u.AddUser()