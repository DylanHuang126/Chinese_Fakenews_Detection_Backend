from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_script import Manager
import datetime
import os
from shared import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + os.path.join(app.root_path, 'demo.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
db.init_app(app)

#with app.app_context():
#    db.create_all()

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

api = Api(app)

from resourses.resource import NewsResource, HotSearchResource, HotSearchAllResource, \
                               SuspectUserResource, StatResource, LoadResource

api.add_resource(NewsResource, '/api/query')
api.add_resource(HotSearchResource, '/api/single_search')
api.add_resource(HotSearchAllResource, '/api/search')
api.add_resource(SuspectUserResource, '/api/suspect_user')
api.add_resource(StatResource, '/api/stat')
api.add_resource(LoadResource, '/api/load_user')


if __name__ == "__main__":
    app.run(debug=True)
