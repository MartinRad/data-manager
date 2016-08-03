from flask import Flask
from flask_login import LoginManager
from datetime import timedelta
import os
from flask.ext.basicauth import BasicAuth
from flask.ext.mongoengine import MongoEngine

UPLOAD_FOLDER = os.getcwd() + '/uploads/'

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'radteam'
app.config['BASIC_AUTH_PASSWORD'] = 'rad0109'
app.config['DEBUG']=True
basic_auth = BasicAuth(app)

login_manager = LoginManager()
login_manager.init_app(app)
app.secret_key = 'putyoursecretkey'
app.permanent_session_lifetime = timedelta(seconds=600)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

from .urls import *
