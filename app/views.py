# -*- coding: utf-8 -*-

import os
import logging
from datetime import datetime, timedelta

import telegram
from telegram import ParseMode
from flask import request, abort

from . import app, db, updater, dispatcher, db_session
from app.src.bot_constants import *
from app.src.utils import *
from app.models import Channel

logger = logging.getLogger()


@app.route('/{0}'.format(app.config['API_TOKEN']), methods=['POST', 'GET'])
def webhook_handler():    
    if request.headers.get('content-type') == 'application/json':
        update = telegram.Update.de_json(request.get_json(force=True),
                                         updater.bot)
        
        if os.environ.get('ON_UPGRADE', False):
            send_response(dispatcher.bot, update,
                          Messages.ON_UPGRADE)
            return '', 200
            
        dispatcher.process_update(update)
        return '', 200
    else:
        abort(403)

@app.route('/{0}/is-healthy'.format(app.config['API_TOKEN']), methods=['POST', 'GET'])
def health_check():
    """ Health checking for nginx
    """ 
    return '', 200
        
@app.route('/{0}/payment-notification'.format(app.config['API_TOKEN']), methods=['POST'])
def receive_payment_notification(): 
    logger.debug('Handling notification with request data {0}'.format(request.json))
       
    status = request.json.get('status')
    user_data = request.json['user_data']
    channel = Channel.query.get(user_data['channel_id'])
    reply_markup = InlineKeyboardMarkup([
        [Buttons.get_button(Commands.MANAGMENT, 
                            label=ButtonsLabels.BACK_TO_MANAGMENT, 
                            channel_id=channel.channel_id, 
                            channel_name=channel.username)]
    ])
    if status == 'success':
        message = ''
        if int(user_data['price_duration']) == PAY_WEEK:
            start_date = datetime.today() if channel.due_date < datetime.today() else channel.due_date
            channel.due_date = start_date + timedelta(days=7)
            timedeltaStr = '7 дней'
        elif int(user_data['price_duration']) == PAY_MONTH:
            start_date = datetime.today() if channel.due_date < datetime.today() else channel.due_date
            channel.due_date = start_date + timedelta(days=31)
            timedeltaStr = '31 день'
        elif int(user_data['price_duration']) == PAY_ALWAYS:
            channel.has_infinite_subsribe = True
            timedeltaStr = 'бессрочно'
        else:
            logging.error('Unexpected price_duration {0}'.format(user_data['price_duration']))
            dispatcher.bot.edit_message_text(
                chat_id=user_data['chat_id'],
                text=Messages.ERROR,
                message_id=user_data['message_id'],
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup
            )
            return '', 400
        
        db_session.add(channel)
        db_session.commit()
        message = '<b>Реферальная программа для канала @{0} продлена на срок</b> - {1}.'.format(
            channel.username, timedeltaStr)
        dispatcher.bot.edit_message_text(
            chat_id=user_data['chat_id'],
            text=message,
            message_id=user_data['message_id'],
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        return '', 200

    elif status == 'refused' or status == 'timeout':
        logger.warning('Payment failed with status {0} for channel {1}'.format(status, channel))
        message = 'К сожалению оплата не увенчилась успехом! Если вы считаете это ошибкой, пожалуйста, ' \
                  'свяжитесь с @miner34006. Спасибо!'
        dispatcher.bot.edit_message_text(
            chat_id=user_data['chat_id'],
            text=message,
            message_id=user_data['message_id'],
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
        return '', 200
    
    logger.error('Unexpected status received <{0}>'.format(status))
    return '', 400

@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return '', 500
