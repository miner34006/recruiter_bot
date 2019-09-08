# -*- coding: utf-8 -*-

import telegram
from flask import request

from . import app, db, updater, dispatcher, API_TOKEN


@app.route('/{0}'.format(API_TOKEN), methods=['POST', 'GET'])
def webhook_handler():
    if request.headers.get('content-type') == 'application/json':
        update = telegram.Update.de_json(request.get_json(force=True),
                                         updater.bot)
        dispatcher.process_update(update)
        return '', 200
    else:
        abort(403)
