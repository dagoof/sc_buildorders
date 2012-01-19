import flask
from flaskext.sqlalchemy import SQLAlchemy

SECRET_KEY = 'devkey'
DEBUG = True
app = flask.Flask(__name__)
app.config.from_object(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trie_build_orders.db'
db = SQLAlchemy(app)

import build_orders.views

