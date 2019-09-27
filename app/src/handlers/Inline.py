# -*- coding: utf-8 -*-

import uuid
import logging
from datetime import datetime

from sqlalchemy import or_
from telegram import InlineKeyboardButton, \
                     InlineQueryResultArticle, \
                     InputTextMessageContent
from telegram.ext import CallbackQueryHandler, InlineQueryHandler

from app import db_session
from app.models import Channel, Inviter, ChannelInviter, Referral
from app.src.bot_constants import *
from app.src.utils import *

logger = logging.getLogger()


class Inline(object):
    @staticmethod
    def add_handlers(dispatcher):
        """Adding inline handlers to dispatcher

        :param dispatcher: dispatcher object
        :type dispatcher: telegram.dispatcher
        """
        dispatcher.add_handler(
            CallbackQueryHandler(
                Inline.join_program,
                pattern='{0}:.+'
                .format(Actions.JOIN_PROGRAM)))

        # Inline show link to channel
        dispatcher.add_handler(
            CallbackQueryHandler(
                Inline.show_link,
                pattern=r'.{60}'))

        # On noncommand i.e message - echo the message on Telegram
        dispatcher.add_handler(
            InlineQueryHandler(
                Inline.inline_query_handler))

    @staticmethod
    def join_program(bot, update):
        """ Add new user to program as referraler

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        username = update.effective_user.username
        user_id = update.effective_user.id

        if not db_session.query(Inviter.inviter_id).filter_by(
                inviter_id=user_id).scalar():
            logger.debug('Adding inviter <{0}> to DB'.format(user_id))
            inviter = Inviter(user_id, username)
            db_session.add(inviter)

        q = db_session.query(ChannelInviter).filter_by(inviter_id=user_id,
                                                       channel_id=channel_id)
        if not db_session.query(q.exists()).scalar():
            logger.info('Adding assoc SI <{0}:{1}> to DB'
                        .format(user_id, channel_id))
            association = ChannelInviter(user_id, channel_id)
            db_session.add(association)

        db_session.commit()
        update.callback_query.answer()

    @staticmethod
    def show_link(bot, update):
        """ Callback function, that added link to the CHANNEL for inline message.
        Function recieve code from update.callback_query.data and uses it for
        determinate channel.

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        code = update.callback_query.data
        inviter_id = db_session.query(ChannelInviter.inviter_id).filter_by(
            code=code).first()[0]
        # If another user pressed the button (not sender)
        # open the link to the channel
        if inviter_id != update.callback_query.from_user.id:
            channel = db_session.query(ChannelInviter).filter_by(
                code=code).first().channel

            # If user not in referrals
            # (not applyed the refferal link yet) add it to DB
            if db_session.query(Referral).filter_by(
                    receiver_id=update.callback_query.from_user.id,
                    channel_id=channel.channel_id).count() == 0:
                db_session.add(Referral(
                    inviter_id, channel.channel_id,
                    receiver_id=update.callback_query.from_user.id))
                db_session.commit()

            button = InlineKeyboardButton(
                ButtonsLabels.GO_TO, url=Links.BASE.format(channel.username))
            keyboard = create_inline_keyboard([button])
            text = Messages.INLINE_LINK_APPERED.format(channel.username)
            update.callback_query.edit_message_text(text=text,
                                                    parse_mode=ParseMode.HTML,
                                                    reply_markup=keyboard)

        return update.callback_query.answer()

    @staticmethod
    def inline_query_handler(bot, update):
        """ Callback function returns all comunities where user is a referaler.
        Callback for inline bot call. User can choose the comunity that he
        wants to recomend in the chat.

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :return: query answer
        :rtype: update.inline_query
        """
        # Get user channels where he is recruiter,
        # and his invite code for this channels
        db_query = db_session.query(Channel.channel_id, Channel.name,
                                    Channel.message, ChannelInviter.code) \
            .join(ChannelInviter,
                  ChannelInviter.channel_id == Channel.channel_id)\
            .filter(Channel.name.startswith(update.inline_query.query),
                    ChannelInviter.inviter_id == update.effective_user.id,
                    Channel.is_running == True,
                    or_(Channel.due_date >= datetime.now(), Channel.has_infinite_subsribe == True))

        results = []
        for channel_id, channel_name, channel_message, code in db_query:
            results.append(
                InlineQueryResultArticle(
                    thumb_url=get_image_url(channel_id, 'logo'),
                    reply_markup=get_inline_keyboard(code),
                    description='Порекомендовать сообщество',
                    id=uuid.uuid4(), title=channel_name,
                    input_message_content=InputTextMessageContent(
                        channel_message + Messages.INLINE_GUIDE,
                        parse_mode=ParseMode.HTML))
            )
        return update.inline_query.answer(results,
                                          is_personal=True,
                                          cache_time=60)

# !UTILS FUNCTIONS

def get_inline_keyboard(unique_code):
    """ Function to get inline keyboard for inline bot first message (SHOW LINK).
    After clicking on this button, we tracked unique code, set +1 for this u
    ser and link to the channel for user.

    :param unique_code: user unique code
    :type unique_code: basestring
    :return: inline keyboard
    :rtype: list
    """
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(ButtonsLabels.SHOW_LINK,
                              callback_data=unique_code)]
    ])
