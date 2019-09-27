# -*- coding: utf-8 -*-

import logging

from telegram.ext.dispatcher import run_async
from telegram.ext import CommandHandler

from app import db_session
from app.models import Channel, Inviter, ChannelInviter, Referral
from app.src.bot_constants import *
from app.src.utils import *

logger = logging.getLogger()


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
        logger.debug('<user:{0}>: starting dialog'.format(update.effective_user.id))
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
        logger.debug('<user:{0}>: show bot help information'.format(update.effective_user.id))
        keyboard = create_inline_keyboard([Buttons.INFORMATION])
        return send_response(bot, update, Messages.HELP, keyboard)
