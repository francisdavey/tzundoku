from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager

tzundoku = Flask(__name__)

tzundoku.config.from_object('config')
db = SQLAlchemy(tzundoku)
lm = LoginManager()
from tzundoku import views, models
lm.init_app(tzundoku)




