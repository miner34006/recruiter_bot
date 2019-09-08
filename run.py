# -*- coding: utf-8 -*-

import time
import os
import sys

from app import app, dispatcher, updater, API_TOKEN

from app.src.handlers.Statistics import Statistics
from app.src.handlers.Main import Main
from app.src.handlers.Inline import Inline
from app.src.handlers.NewChannel import NewChannel
from app.src.handlers.Managment import Managment


reload(sys)
sys.setdefaultencoding('utf8')

SERTIFICATE = os.environ.get(
    'SERTIFICATE', '/etc/ssl/www.recruiter-bot.ru.crt')
PORT = int(os.environ.get('PORT', '5001'))
BALANCER_IP = os.environ.get('BALANCER_IP', '159.65.57.62')

updater.bot.delete_webhook()
updater.bot.set_webhook('https://{0}:443/{1}'.format(BALANCER_IP, API_TOKEN),
                        certificate=open(SERTIFICATE, 'rb'))


if __name__ == '__main__':
    Main.add_handlers(dispatcher)
    Statistics.add_handlers(dispatcher)
    NewChannel.add_handlers(dispatcher)
    Managment.add_handlers(dispatcher)
    Inline.add_handlers(dispatcher)

    time.sleep(3)
    app.run(host='0.0.0.0', port=PORT)
