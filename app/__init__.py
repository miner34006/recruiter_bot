# -*- coding: utf-8 -*-

import os
import sys
import logging

from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from telegram.ext import Updater

from configuration import *


os.environ['PYTHONIOENCODING'] = "utf-8"

app = Flask('recruiter')

FORMAT = u'%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s'
root = logging.getLogger()
logging.basicConfig(format=FORMAT, level=logging.DEBUG,
                    handlers=[logging.FileHandler('/var/log/recruiter_bot.log.debug',
                                                  encoding='utf-8')])

sHandler = logging.StreamHandler()
sHandler.setFormatter(logging.Formatter(FORMAT))

#!PRODUCTION CONFIGURATION
if os.environ.get('PRODUCTION'):
    app.config.from_object(ProductionConfig())
    sHandler.setLevel(logging.INFO)
    root.addHandler(sHandler)

#! DEBUG CONFIGURATION
else:
    app.config.from_object(DevelopmentConfig())
    sHandler.setLevel(logging.DEBUG)
    root.addHandler(sHandler)

db = SQLAlchemy(app)
db_session = db.session

from app.models import *

migrate = Migrate(app, db)

updater = Updater(token=app.config['API_TOKEN'])
dispatcher = updater.dispatcher

webhook = updater.bot.get_webhook_info()
if APPLICATION_IP not in webhook.url:
    updater.bot.delete_webhook()
    updater.bot.set_webhook('https://{0}:{1}/{2}'.format(APPLICATION_IP, RESERVE_PROXY_PORT, app.config['API_TOKEN']),
                            certificate=open(app.config['SERTIFICATE'], 'rb'))

from app.src.handlers.Statistics import Statistics
from app.src.handlers.Main import Main
from app.src.handlers.Inline import Inline
from app.src.handlers.NewChannel import NewChannel
from app.src.handlers.Managment import Managment
from app.src.handlers.Payment import Payment

Main.add_handlers(dispatcher)
Statistics.add_handlers(dispatcher)
NewChannel.add_handlers(dispatcher)
Managment.add_handlers(dispatcher)
Inline.add_handlers(dispatcher)
Payment.add_handlers(dispatcher)

from app.views import *
