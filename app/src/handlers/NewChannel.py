# -*- coding: utf-8 -*-

import logging

from telegram.ext import CommandHandler, ConversationHandler, \
                         MessageHandler, Filters

from app import db_session
from app.models import Channel, Inviter, ChannelInviter, Referral
from app.src.bot_constants import *
from app.src.utils import *

logger = logging.getLogger()
FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - ' \
         '%(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)

GET_FORWARDED = 0


class NewChannel(object):
    @staticmethod
    def add_handlers(dispatcher):
        """Adding add channel handlers to dispatcher

        :param dispatcher: dispatcher object
        :type dispatcher: telegram.dispatcher
        """
        dispatcher.add_handler(ConversationHandler(
            entry_points=[CommandHandler(Commands.ADD,
                                         NewChannel.add_channel)],
            states={
                GET_FORWARDED: [MessageHandler(Filters.forwarded,
                                               NewChannel.receive_forwarded)]
            },
            fallbacks=[CommandHandler(Commands.CANCEL,
                                      NewChannel.cancel_adding)]
        ))

    @staticmethod
    def cancel_adding(bot, update):
        """ Function to cancel adding new channel conversation with user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        send_response(bot, update, Messages.CANCEL_REFERRAL)
        return ConversationHandler.END

    @staticmethod
    def add_channel(bot, update):
        """ Starting create referral program procedure with user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        send_response(bot, update, Messages.CHANNEL_ADD)
        return GET_FORWARDED

    # @staticmethod
    # def not_forwarded(bot, update):
    #     """ Message for user that his message is not message from channel

    #     :param bot: bot
    #     :type bot: telegram.Bot
    #     :param update: update event
    #     :type update: relegram.Update
    #     """
    #     logger.warning('Not a forwarded message was received')
    #     send_response(bot, update, Messages.NOT_CHANNEL_MESSAGE)
    #     return GET_FORWARDED

    @staticmethod
    def receive_forwarded(bot, update):
        """ Receiving forwarding message with channel info

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        user_id = update.message.from_user.id

        if not update.message.forward_from_chat:
            logger.warning('Forwarded, but not a cahnnel message was received')
            send_response(bot, update, Messages.NOT_CHANNEL_MESSAGE)
            return GET_FORWARDED

        channel_username = update.message.forward_from_chat.username
        if not channel_username:
            send_response(bot, update, Messages.CHANNEL_HAS_NO_NAME)
            return GET_FORWARDED

        channel_id = update.message.forward_from_chat.id
        logger.info('User <{0}> send forwarded message from channel <{1}>'
                    .format(user_id, channel_id))
        try:
            chat_admins = [
                admin.user.id
                for admin in bot.get_chat_administrators(channel_id)
            ]
            logger.info('Channel admins: <{0}>'.format(chat_admins))

            if user_id not in chat_admins:
                logger.warning('Could not find user <{0}> in channel admins'
                               .format(user_id))
                send_response(bot, update, Messages.USER_NOT_ADMIN)
                return GET_FORWARDED

            if Channel.exists_in_db(channel_id):
                logger.warning('Channel has already presented in DB')
                send_response(bot, update, Messages.CHANNEL_ALREADY_IN_DB)
                return GET_FORWARDED

            name = update.message.forward_from_chat.title
            channel = Channel(channel_id, channel_username, name,
                              update.message.from_user.username)
            db_session.add(channel)
            db_session.commit()

            # Downloading channel logo to image controller
            logo_url = get_channel_logo(bot, channel_id)
            if logo_url:
                download_image(logo_url, channel_id, 'logo')

            send_response(bot, update, Messages.CHANNEL_ADD_SUCCESS
                          .format(channel_username,
                                  channel.due_date.strftime("%d-%m-%Y %H.%M")))

            return ConversationHandler.END

        except BadRequest as err:
            logger.warning('Failed to get channel admins, reason: {0}'
                           .format(err))
            send_response(bot, update, Messages.NOT_IN_ADMINS_LIST)
            return GET_FORWARDED
