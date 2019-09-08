# -*- coding: utf-8 -*-

import os
import csv
import logging

import telegram
from telegram.ext import CommandHandler, CallbackQueryHandler, \
                         ConversationHandler

from app import db_session
from app.models import Channel, Inviter, ChannelInviter, Referral
from app.src.bot_constants import *
from app.src.utils import *

logger = logging.getLogger()
FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - ' \
         '%(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)


class Statistics(object):
    @staticmethod
    def add_handlers(dispatcher):
        """Adding statistics handlers to dispatcher

        :param dispatcher: dispatcher object
        :type dispatcher: telegram.dispatcher
        """
        dispatcher.add_handler(CommandHandler(
            Commands.STATISTICS,
            Statistics.list_statistics))
        dispatcher.add_handler(CallbackQueryHandler(
            Statistics.list_statistics,
            pattern=Actions.STATISTICS_LIST))
        dispatcher.add_handler(CallbackQueryHandler(
            Statistics.channel_statisctics,
            pattern='{0}:.+'
            .format(Commands.STATISTICS)))
        dispatcher.add_handler(CallbackQueryHandler(
            Statistics.channel_clear,
            pattern='{0}:.+'
            .format(Actions.CLEAR)))
        dispatcher.add_handler(CallbackQueryHandler(
            Statistics.full_channel_statistics,
            pattern='{0}:.+'
            .format(Actions.FULL_STATS)))

    @staticmethod
    def list_statistics(bot, update):
        """ Send or edit last message with channels for statistics purpose

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        username = update.effective_user.username
        channels = db_session.query(Channel).filter_by(admin=username)
        if not db_session.query(channels.exists()).scalar():
            logger.info('User <{0}> has no channels for statistics'
                        .format(username))
            return send_response(bot, update, Messages.NO_REFERRAL_CHANNELS)

        buttons = [InlineKeyboardButton(channel.username,
                                        callback_data='{0}:{1}:{2}'
                                        .format(Commands.STATISTICS,
                                                channel.channel_id,
                                                channel.username))
                   for channel in channels]

        return send_response(bot, update,
                             get_user_sattistics_text(channels),
                             create_inline_keyboard(buttons, width=3))

    @staticmethod
    def channel_statisctics(bot, update):
        """ Show user all available channel statistics

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')

        new_users_count, top_users_stats = get_channel_statistics(bot,
                                                                  channel_id,
                                                                  db_session)
        if len(top_users_stats) > 5:
            top_users_stats = top_users_stats[5:]

        report_text = get_channel_statistics_text(new_users_count,
                                                  top_users_stats,
                                                  channel_name)
        keyboard = InlineKeyboardMarkup([
            [Buttons.get_button(Actions.FULL_STATS,
                                ButtonsLabels.FULL_STATS,
                                channel_id, channel_name),
             Buttons.get_button(Actions.CLEAR, ButtonsLabels.CLEAR_STATISTICS,
                                channel_id, channel_name)],
            [Buttons.BACK(Actions.STATISTICS_LIST)]
        ])
        return send_response(bot, update, report_text, keyboard)

    @staticmethod
    def full_channel_statistics(bot, update):
        """ Get full channel statistics via file

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        _, csv_data = get_channel_statistics(bot, channel_id, db_session)

        csv_data.insert(0, ['username', 'invited_users_count'])

        csv_file_path = '/tmp/{0}.csv'.format(channel_name)
        with open(csv_file_path, 'w') as csvFile:
            writer = csv.writer(csvFile)
            writer.writerows(csv_data)
            csvFile.close()
            os.chmod(csv_file_path, 0o755)

        bot.send_document(chat_id=update.effective_chat.id,
                          document=open(csv_file_path, 'rb'))
        os.remove(csv_file_path)
        update.callback_query.answer()

    @staticmethod
    def channel_clear(bot, update):
        """ Clear statistics data of the selected channel

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        Referral.query.filter(Referral.channel_id == channel_id).delete()
        db_session.commit()
        return Statistics.channel_statisctics(bot, update)


# !UTILS FUNCTIONS

def get_channel_statistics(bot, channel_id, db_session):
    """ Get information about channel referral program

    :param channel_id: telegram channel id
    :type channel_id: int
    :param db_session: DB session
    :type db_session: session
    :return: total count of new users, top referrals
    :rtype: tuple
    """
    new_users = set(Referral.get_new_users(bot, channel_id))
    logger.debug('New users from referral program <{0}>'.format(new_users))
    top_users = db_session \
        .query(Referral.inviter_id, Inviter.name) \
        .join(Inviter, Referral.inviter_id == Inviter.inviter_id) \
        .filter(Referral.channel_id == channel_id) \
        .group_by(Referral.inviter_id, Inviter.name) \
        .order_by(Referral.inviter_id.desc())

    top_users_stats = []
    for user_id, username in top_users:
        invited_users = [id for id, in db_session.query(Referral.receiver_id)
                         .filter_by(inviter_id=user_id)]
        invited_users = len(set(invited_users) & new_users)
        if invited_users:
            top_users_stats.append((username, invited_users))

    top_users_stats = sorted(top_users_stats,
                             key=lambda data: data[1],
                             reverse=True)
    logger.debug('Top users statistics <{0}>'.format(top_users_stats))
    return len(new_users), top_users_stats


def get_user_sattistics_text(channels):
    """ Get message for summary statistics screen

    :param channels: list with channel information
    :type channels: list
    :return: message to send to user
    :rtype: str
    """
    channelsInfo = ''
    for index, channel in enumerate(channels, start=1):
        channelsInfo += '{0}. @{1}\n'.format(index, channel.username)
    channelsInfo = 'Сообщества, в которых запущена рекрутская программа:' \
                   '\n{0}'.format(channelsInfo)
    return '{0}\n{1}'.format(channelsInfo, Messages.SELECT_CHANNEL)


def get_channel_statistics_text(new_users_count, top_users, channel_name):
    """ Create report for current channel statistics

    :param new_users_count: total new users
    :type new_users_count: int
    :param top_users: top users
    :type top_users: list
    :param channel_name: header channel name
    :type channel_name: basestring
    :return: report text
    :rtype: basestring
    """
    report_text = Messages.HEADER.format(channel_name)
    report_text += 'Всего к каналу присоединилось <b>{0}</b> пользователей.' \
                   '\n\n'.format(new_users_count)
    if top_users:
        report_text += '<b>Топ активных рекрутеров</b>:\n'
        for index, user_data in enumerate(top_users, start=1):
            report_text += '{0}. @{1} пригласил {2};\n'.format(index,
                                                               user_data[0],
                                                               user_data[1])

    return report_text
