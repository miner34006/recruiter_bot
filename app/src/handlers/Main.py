# -*- coding: utf-8 -*-

import logging

from telegram.ext import CommandHandler

from app import db_session
from app.models import Channel, Inviter, ChannelInviter, Referral
from app.src.bot_constants import *
from app.src.utils import *

logger = logging.getLogger()
FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s -' \
         ' %(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)


class Main(object):
    @staticmethod
    def add_handlers(dispatcher):
        """Adding main handlers to dispatcher

        :param dispatcher: dispatcher object
        :type dispatcher: telegram.dispatcher
        """
        dispatcher.add_handler(CommandHandler(Commands.START,
                                              Main.start_dialog))
        dispatcher.add_handler(CommandHandler(Commands.HELP,
                                              Main.available_actions))

    @staticmethod
    def start_dialog(bot, update):
        """ Send start message info to user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        keyboard = create_inline_keyboard([Buttons.INFORMATION])
        message = Messages.HELLO + Messages.HELP
        return send_response(bot, update, message, keyboard)

    @staticmethod
    def available_actions(bot, update):
        """ Send help message with commands to user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        keyboard = create_inline_keyboard([Buttons.INFORMATION])
        return send_response(bot, update, Messages.HELP, keyboard)
