# -*- coding: utf-8 -*-

import urllib
import logging
import math

import requests
from telegram import InlineKeyboardButton, \
                     InlineQueryResultArticle, \
                     InputTextMessageContent
from telegram.ext import CallbackQueryHandler, InlineQueryHandler, \
                         ConversationHandler, CommandHandler

from app import app, db_session, PAYMENT_SERVICE_IP, PAYMENT_SERVICE_PORT, \
                                 APPLICATION_IP, RESERVE_PROXY_PORT
from app.models import Channel, Inviter, ChannelInviter, Referral
from app.src.handlers.Managment import Managment
from app.src.bot_constants import *
from app.src.utils import *

logger = logging.getLogger()


class Payment(object):
    @staticmethod
    def add_handlers(dispatcher):
        """Adding payment handlers to dispatcher

        :param dispatcher: dispatcher object
        :type dispatcher: telegram.dispatcher
        """
        dispatcher.add_handler(CallbackQueryHandler(
                    Payment.start_payment,
                    pattern='{0}:.+'.format(Actions.START_PAYMENT)))
        dispatcher.add_handler(CallbackQueryHandler(
                    Payment.process_payment,
                    pattern='{0}:.+'.format(Actions.PROCESS_PAYMENT)))
        
    
    @staticmethod
    @admin_required
    def start_payment(bot, update):
        """ Start payment dialog with user, send available payment options 
        in the button labels (week, month, always)

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        members_count = bot.get_chat_members_count(channel_id)
        if members_count > 16000:
            keyboard = InlineKeyboardMarkup([
                [Buttons.get_button(Commands.MANAGMENT, ButtonsLabels.BACK, channel_id, channel_name)], 
            ])
            return send_response(bot, update, Messages.TOO_MANY_MEMBERS, keyboard)
            
        keyboard = InlineKeyboardMarkup([
            get_price_buttons(members_count, channel_id, channel_name),
            [Buttons.get_button(
                Commands.MANAGMENT, ButtonsLabels.BACK, channel_id, channel_name)], 
        ])
        return send_response(bot, update, Messages.SELECT_PAYMENT_OPTION, keyboard)
    
    @staticmethod
    @admin_required
    def process_payment(bot, update):
        """ Start payment dialog with user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name, price_duration, amount = update.callback_query.data.split(':')
        
        # Getting payment url from paymentService
        response = None
        try:
            url = 'http://{0}:{1}/payment'.format(PAYMENT_SERVICE_IP, PAYMENT_SERVICE_PORT)
            response = requests.post(url, json={'amount': amount, 'merchant_id': channel_id})                
        except Exception as err:
            logger.error('Failed to get payment url from payment service. Reason: {0}'.format(err))
            send_response(bot, update, Messages.ERROR)
            update.message = True
            update.callback_query.data = ':{0}:{1}:'.format(channel_id, channel_name)
            return Managment.channel_managment(bot, update)
            
        payment_url = response.json()['payment_url']
        payment_id = response.json()['id']
        # Create notification for this payment
        try:
            url = 'http://{0}:{1}/payment/{2}/notify'.format(PAYMENT_SERVICE_IP, PAYMENT_SERVICE_PORT, payment_id)
            user_data = {
                'channel_id': channel_id,
                'channel_name': channel_name,
                'price_duration': price_duration,
                'amount': amount,
                'message_id': update.effective_message.message_id,
                'chat_id': update.effective_chat.id,
            }
            notification_url = 'https://{0}:{1}/{2}/payment-notification'.format(APPLICATION_IP, RESERVE_PROXY_PORT,
                                                                                 app.config['API_TOKEN'])
            data = {'notification_url': notification_url, 'user_data': user_data}
            response = requests.post(url, json=data)
        except Exception as err:
            logger.error('Failed create notification. Reason: {0}'.format(err))
            send_response(bot, update, Messages.ERROR)
            update.message = True
            update.callback_query.data = ':{0}:{1}:'.format(channel_id, channel_name)
            return Managment.channel_managment(bot, update)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                ButtonsLabels.PAY, url=payment_url)],
            [Buttons.get_button(
                Actions.START_PAYMENT, ButtonsLabels.BACK, channel_id, channel_name)
        ]])
        send_response(bot, update, Messages.PUSH_BUTTON_TO_PAY, keyboard)
    

# !UTILS FUNCTIONS

def get_price_buttons(members_count, channel_id, channel_name):
    # Week price
    percent = 0.15
    price1 = int(math.ceil(float(members_count)/100) * 100 * percent + 100)
    price1 = price1 if price1 < 15000 else 15000
    # Month price
    percent = 0.45
    price2 = int(math.ceil(float(members_count)/100) * 100 * percent + 100)
    price2 = price2 if price2 < 15000 else 15000
    # Infinite price
    percent = 0.9
    price3 = int(math.ceil(float(members_count)/100) * 100 * percent + 100)
    price3 = price3 if price3 < 15000 else 15000
      
    return [
        Buttons.get_button(
            Actions.PROCESS_PAYMENT, 
            '{0}₽ - Неделя'.format(price1), 
            channel_id, channel_name, 
            PAY_WEEK, price1),
        Buttons.get_button(
            Actions.PROCESS_PAYMENT, 
            '{0}₽ - месяц'.format(price2),
            channel_id, channel_name, 
            PAY_MONTH, price2),
        Buttons.get_button(
            Actions.PROCESS_PAYMENT, 
            '{0}₽ - бессрочно'.format(price3),
            channel_id, channel_name, 
            PAY_ALWAYS, price3),
    ]
