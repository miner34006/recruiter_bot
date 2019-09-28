# -*- coding: utf-8 -*-

import logging
import os

if not os.environ.get('PRODUCTION'):
    from pathlib import Path
    from dotenv import load_dotenv
    env_path = Path('./deployment/') / '.env'
    load_dotenv(dotenv_path=env_path)


APPLICATION_IP = os.environ.get('APPLICATION_IP')
APPLICATION_PORT = int(os.environ.get('APPLICATION_PORT'))

RESERVE_PROXY_PORT = os.environ.get('RESERVE_PROXY_PORT')
if not RESERVE_PROXY_PORT:
    RESERVE_PROXY_PORT = APPLICATION_PORT

IMAGE_CONTROLLER_PORT = os.environ.get('IMAGE_CONTROLLER_PORT')
IMAGE_CONTROLLER_IP = os.environ.get('IMAGE_CONTROLLER_IP')

PAYMENT_SERVICE_PORT = os.environ.get('PAYMENT_SERVICE_PORT')
PAYMENT_SERVICE_IP = os.environ.get('PAYMENT_SERVICE_IP')


class Config(object):
    DEBUG = False
    TESTING = False
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://referraldb_dev:Password123!@localhost:5432/referraldb_dev'

    SERTIFICATE = '/etc/ssl/www.recruiter-bot.ru.crt'
    API_TOKEN = os.environ.get('API_TOKEN')
    
class ProductionConfig(Config):
    POSTGRES_DB = os.environ.get('POSTGRES_DB')
    POSTGRES_IP = os.environ.get('POSTGRES_IP')
    POSTGRES_PORT = os.environ.get('POSTGRES_PORT')
    POSTGRES_USER = os.environ.get('POSTGRES_USER')
    POSTGRES_PASSWORD = os.environ.get('POSTGRES_PASSWORD')
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{4}:{2}/{3}'.format(
        POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_DB, POSTGRES_IP)

class DevelopmentConfig(Config):
    DEBUG = True
