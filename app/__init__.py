# -*- coding: utf-8 -*-

import os
import sys

from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from telegram.ext import Updater

API_TOKEN = os.environ.get('API_TOKEN',
                           "983431171:AAHLApwpzQeTEK1Sf3OtFb-j5elN5HxzwxQ")

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
db_session = db.session

updater = Updater(token=API_TOKEN)
dispatcher = updater.dispatcher

from app.views import *

db.create_all()
