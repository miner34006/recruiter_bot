# -*- coding: utf-8 -*-

from functools import partial
from datetime import datetime, timedelta
import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CommandHandler, CallbackQueryHandler, \
                         ConversationHandler, MessageHandler, Filters

from app import db_session
from app.models import Channel, Inviter, ChannelInviter, Referral
from app.src.bot_constants import *
from app.src.utils import *

logger = logging.getLogger('root')
FORMAT = '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - ' \
         '%(funcName)s: %(message)s'
logging.basicConfig(format=FORMAT)
logger.setLevel(logging.DEBUG)


def payment_required(finish_conversation=False):
    def decorator(function):
        def wrapper(bot, update, *args, **kwargs):
            _, channel_id, channel_name = update.callback_query.data.split(':')
            channel = Channel.query.get(channel_id)
            if need_payment(channel):
                keyboard = get_need_payment_keyboard(
                    channel_id, channel_name)
                send_response(bot, update,
                              Messages.NEED_PAYMENT,
                              keyboard)
                if finish_conversation:
                    return ConversationHandler.END
                return
            return function(bot, update, *args, **kwargs)
        return wrapper
    return decorator


class Managment(object):
    @staticmethod
    def add_handlers(dispatcher):
        """Adding managment handlers to dispatcher

        :param dispatcher: dispatcher object
        :type dispatcher: telegram.dispatcher
        """
        # Publishing post into the channel
        dispatcher.add_handler(ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    Managment.create_post,
                    pattern='{0}:.+'.format(Actions.CREATE_POST),
                    pass_user_data=True)],
            states={
                States.GET_POST_DATA: [
                    MessageHandler(
                        (Filters.text & ~ Filters.command),
                        Managment.receive_post_text,
                        pass_user_data=True),
                    MessageHandler(
                        Filters.photo,
                        Managment.receive_post_photo,
                        pass_user_data=True)
                ],
            },
            fallbacks=[CommandHandler(
                Commands.CANCEL,
                Managment.cancel_post,
                pass_user_data=True)]
        ), group=0)

        # Changing referral message
        dispatcher.add_handler(ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    Managment.create_message,
                    pattern='{0}:.+'.format(Actions.CREATE_MESSAGE),
                    pass_user_data=True)],
            states={
                States.GET_MESSAGE: [
                    MessageHandler(
                        (Filters.text & ~ Filters.command),
                        Managment.receive_message,
                        pass_user_data=True)],
            },
            fallbacks=[CommandHandler(
                Commands.CANCEL,
                Managment.cancel_message,
                pass_user_data=True)]
        ), group=1)

        dispatcher.add_handler(
            CommandHandler(
                Commands.MANAGMENT,
                Managment.list_managment))
        dispatcher.add_handler(
            CallbackQueryHandler(
                Managment.dummy_function,
                pattern=Actions.DUMMY))
        dispatcher.add_handler(
            CallbackQueryHandler(
                Managment.list_managment,
                pattern=Actions.MANAGMENT_LIST))
        dispatcher.add_handler(
            CallbackQueryHandler(
                Managment.channel_managment,
                pattern='{0}:.+'.format(Commands.MANAGMENT)))
        dispatcher.add_handler(
            CallbackQueryHandler(
                Managment.managment_help,
                pattern='{0}:.+'.format(Actions.MANAGEMENT_HELP)))
        dispatcher.add_handler(
            CallbackQueryHandler(
                partial(Managment.change_referral_state, is_running=True),
                pattern='{0}:.+'.format(Actions.START_REFERRAL)))
        dispatcher.add_handler(
            CallbackQueryHandler(
                partial(Managment.change_referral_state, is_running=False),
                pattern='{0}:.+'.format(Actions.STOP_REFERRAL)))

    @staticmethod
    def list_managment(bot, update):
        """ Send or edit last message with channels list for managment purpose

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        username = update.effective_user.username
        channels = db_session.query(Channel).filter_by(admin=username)
        if not db_session.query(channels.exists()).scalar():
            logger.info('User <{0}> has no channels for managment'
                        .format(username))
            return send_response(bot, update, Messages.NO_REFERRAL_CHANNELS)

        buttons = [
            InlineKeyboardButton(channel.username,
                                 callback_data='{0}:{1}:{2}'
                                 .format(Commands.MANAGMENT,
                                         channel.channel_id,
                                         channel.username))
            for channel in channels
        ]
        keyboard = create_inline_keyboard(buttons, width=3)
        return send_response(bot,
                             update,
                             Messages.SELECT_CHANNEL_TO_MANAGE,
                             keyboard)

    @staticmethod
    @payment_required()
    def channel_managment(bot, update):
        """ Show user all available managment actions with current channel settings:
        1. Start referral program;
        2. Stop referral program;
        4. Setting the referral message;
        5. Publish post in channel;

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        channel = Channel.query.get(channel_id)
        keyboard = get_managment_keyboard(channel_id, channel_name)
        text = get_managment_statistics(channel_name, channel.due_date,
                                        channel.is_running, channel.message)
        return send_response(bot, update, text, keyboard)

    @staticmethod
    def managment_help(bot, update):
        """ Show user managment options help information (description)

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')

        channel = Channel.query.get(channel_id)
        if need_payment(channel):
            keyboard = get_need_payment_keyboard(channel_id,
                                                 channel_name)
        else:
            keyboard = get_managment_keyboard(channel_id,
                                              channel_name)

        return send_response(bot, update, Messages.MANAGMENT_HELP, keyboard)

    @staticmethod
    @payment_required()
    def change_referral_state(bot, update, is_running):
        """ Stopping referral program by stop managment button

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        channel = Channel.query.get(channel_id)

        channel.is_running = is_running
        db_session.add(channel)
        db_session.commit()

        return Managment.channel_managment(bot, update)

    @staticmethod
    @payment_required(finish_conversation=True)
    def create_message(bot, update, user_data):
        """ Handler to start message creation procedure with user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        channel = Channel.query.get(channel_id)

        update.callback_query.answer()

        text = Messages.MESSAGE_ADD.format(channel_name)
        keyboard = [[ButtonsLabels.PREREVIEW], [ButtonsLabels.CANCEL,
                                                ButtonsLabels.SAVE]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=text,
                         reply_markup=reply_markup)

        user_data['message'] = channel.message
        user_data['channel'] = channel
        return States.GET_MESSAGE

    @staticmethod
    def save_message(bot, update, user_data):
        """ Save "hi message" according to user input

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        channel = user_data['channel']
        channel.message = user_data['message']
        db_session.add(channel)
        db_session.commit()
        send_response(bot, update, Messages.SAVE_MESSAGE,
                      ReplyKeyboardRemove())

        keyboard = get_managment_keyboard(channel.channel_id,
                                          channel.username)
        text = get_managment_statistics(channel.username, channel.due_date,
                                        channel.is_running, channel.message)
        send_response(bot, update, text, keyboard)

        return ConversationHandler.END

    @staticmethod
    def cancel_message(bot, update, user_data):
        """ Cancel message creation anf go to managment screen

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=Messages.CANCEL_MESSAGE,
                         reply_markup=ReplyKeyboardRemove())

        channel = user_data['channel']
        keyboard = get_managment_keyboard(channel.channel_id,
                                          channel.username)
        text = get_managment_statistics(channel.username, channel.due_date,
                                        channel.is_running, channel.message)
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=text,
                         reply_markup=keyboard)

        return ConversationHandler.END

    @staticmethod
    def preview_message(bot, update, user_data):
        """ Preview "hi message" according to previous user input

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        new_message = user_data['message']
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(ButtonsLabels.SHOW_LINK,
                                  callback_data=Actions.DUMMY)]
        ])
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=new_message.encode('utf-8'),
                         reply_markup=keyboard)

        return States.GET_MESSAGE

    @staticmethod
    def receive_message(bot, update, user_data):
        """ Function handles message creation dialog with user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        user_message = update.effective_message.text
        if user_message == ButtonsLabels.PREREVIEW.decode('utf-8'):
            return Managment.preview_message(bot, update, user_data)
        if user_message == ButtonsLabels.CANCEL.decode('utf-8'):
            return Managment.cancel_message(bot, update, user_data)
        if user_message == ButtonsLabels.SAVE.decode('utf-8'):
            return Managment.save_message(bot, update, user_data)

        if len(update.effective_message.text) > MAXIMUM_INLINE_LENGTH:
            bot.send_message(chat_id=update.effective_chat.id,
                             parse_mode=ParseMode.HTML,
                             text=Messages.MORE_THAN_MAXIMUM_LENGTH)
            return States.GET_MESSAGE

        user_data['message'] = update.effective_message.text
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=Messages.RECEIVED)
        return States.GET_MESSAGE

    @staticmethod
    def dummy_function(bot, update):
        """ Dummy function (do nothing)

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        """
        update.callback_query.answer()

    @staticmethod
    @payment_required(finish_conversation=True)
    def create_post(bot, update, user_data):
        """ Creating post message for user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        _, channel_id, channel_name = update.callback_query.data.split(':')
        channel = Channel.query.get(channel_id)

        update.callback_query.answer()

        reply_markup = ReplyKeyboardMarkup(
            [[ButtonsLabels.PREREVIEW], [ButtonsLabels.CANCEL,
                                         ButtonsLabels.PUBLISH]],
            resize_keyboard=True)
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=Messages.POST_CREATION.format(channel_name),
                         reply_markup=reply_markup)

        user_data.clear()
        user_data['channel'] = channel
        return States.GET_POST_DATA

    @staticmethod
    def preview_post(bot, update, user_data):
        """ Send post preview to user

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        post_text = user_data.get('text')
        post_image = user_data.get('image')
        if not post_text and not post_image:
            bot.send_message(chat_id=update.effective_chat.id,
                             parse_mode=ParseMode.HTML,
                             text=Messages.NOTHING_TO_PREVIEW)
            return States.GET_POST_DATA

        text, reply_markup = get_post(post_text, post_image)
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=text,
                         reply_markup=reply_markup,
                         disable_web_page_preview=False)

        return States.GET_POST_DATA

    @staticmethod
    def publish_post(bot, update, user_data):
        """ Publishing post in channel and close the conversation

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        post_text = user_data.get('text')
        post_image = user_data.get('image')
        if not post_text and not post_image:
            bot.send_message(chat_id=update.effective_chat.id,
                             parse_mode=ParseMode.HTML,
                             text=Messages.NOTHING_TO_PUBLISH)
            return States.GET_POST_DATA

        # Publish information post in channel
        channel = user_data['channel']
        callback_data = '{0}:{1}:{2}'\
                        .format(Actions.JOIN_PROGRAM,
                                channel.channel_id,
                                channel.username)
        text, reply_markup = get_post(post_text, post_image, callback_data)
        bot.send_message(chat_id=channel.channel_id,
                         parse_mode=ParseMode.HTML,
                         text=text,
                         reply_markup=reply_markup,
                         disable_web_page_preview=False)

        # Notify user that information post was published
        send_response(bot, update, Messages.PUBLISH_POST,
                      ReplyKeyboardRemove())

        # Send user managment message with channel actions
        keyboard = get_managment_keyboard(channel.channel_id,
                                          channel.username)
        text = get_managment_statistics(channel.username,
                                        channel.due_date,
                                        channel.is_running,
                                        channel.message)
        send_response(bot, update, text, keyboard)
        return ConversationHandler.END

    @staticmethod
    def receive_post_text(bot, update, user_data):
        """ Handler for text messages in post creation dialog

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        user_message = update.effective_message.text
        if user_message == ButtonsLabels.PREREVIEW.decode('utf-8'):
            return Managment.preview_post(bot, update, user_data)
        if user_message == ButtonsLabels.CANCEL.decode('utf-8'):
            return Managment.cancel_post(bot, update, user_data)
        if user_message == ButtonsLabels.PUBLISH.decode('utf-8'):
            return Managment.publish_post(bot, update, user_data)

        user_data['text'] = user_message
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=Messages.RECEIVED)
        return States.GET_POST_DATA

    @staticmethod
    def receive_post_photo(bot, update, user_data):
        """ Handler when post image received

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        channel = user_data['channel']

        file_id = update.message.photo[0].file_id
        file_url = bot.get_file(file_id).file_path

        user_data['image'] = download_image(file_url, file_id, 'post')
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=Messages.RECEIVED)
        return States.GET_POST_DATA

    @staticmethod
    def cancel_post(bot, update, user_data):
        """ Cancel message creation anf go to managment screen

        :param bot: bot
        :type bot: telegram.Bot
        :param update: update event
        :type update: relegram.Update
        :param user_data: user data from conversation
        :type user_data: dict
        """
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=Messages.CANCEL_POST_CREATION,
                         reply_markup=ReplyKeyboardRemove())

        channel = user_data['channel']
        keyboard = get_managment_keyboard(channel.channel_id,
                                          channel.username)
        text = get_managment_statistics(channel.username,
                                        channel.due_date,
                                        channel.is_running,
                                        channel.message)
        bot.send_message(chat_id=update.effective_chat.id,
                         parse_mode=ParseMode.HTML,
                         text=text,
                         reply_markup=keyboard)

        return ConversationHandler.END


# !UTILS FUNCTIONS

def get_managment_statistics(channel_name, due_date, is_running, message):
    """ Create statistics meesage for current channel managment message

    :param channel_name: chanel name
    :type channel_name: basestring
    :param due_date: due date not needed payment
    :type due_date: datetime
    :param is_running: is this channel program is running
    :type is_running: bool
    :param message: "hi" message
    :type message: basestring
    :return: message to send to user
    :rtype: str
    """
    header = Messages.HEADER.format(channel_name)
    status = 'ИДЕТ РЕКРУТИНГ ✅' if is_running else 'РЕКРУТИНГ ОСТАНОВЛЕН ⛔️'
    return '{0}' \
           '▶️ Рекрутская программа оплачена до <b>{1}</b>\n\n' \
           '▶️ Текущее состояние - <b>{2}</b>\n\n' \
           '️🔽 <b>Сообщение рекрутеров</b> 🔽\n{3}' \
           .format(header,
                   due_date.strftime("%d-%m-%Y %H.%M"),
                   status,
                   message.encode('utf-8'))


def need_payment(channel):
    """ Check channel need payment

    :param channel: channel to check
    :type channel: Channel
    :return: channel needs payment
    :rtype: bool
    """
    return datetime.now() > channel.due_date


def get_post(message, img_url, inline_button_callback=None):
    """ Get post data for publishing

    :param message: message to publish
    :type message: basestring
    :param img_url: url to publish
    :type img_url: basestring
    :param inline_button_callback: callback for button, defaults to None
    :type inline_button_callback: basestring, optional
    :return: text with keyboard
    :rtype: tuple
    """
    callback_data = inline_button_callback or Actions.DUMMY
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(ButtonsLabels.JOIN_PROGRAM,
                              callback_data=callback_data)]
    ])
    if not message and img_url:
        message = '.'

    text = '{0} <a href="{1}">&#8205;</a>'.format(
        message.encode('utf-8'), img_url)
    return text, keyboard


def get_managment_keyboard(channel_id, channel_name):
    """ Building main managment keyboard

    :param channel_id: channel id
    :type channel_id: basestring
    :param channel_name: channel name
    :type channel_name: basestring
    :return: InlineKeyboardMarkup
    :rtype: telegram.InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup([
        [Buttons.get_button(
            Actions.START_REFERRAL,
            ButtonsLabels.START_REFERRAL,
            channel_id, channel_name),
            Buttons.get_button(
            Actions.STOP_REFERRAL,
            ButtonsLabels.STOP_REFERRAL,
            channel_id, channel_name)],
        [Buttons.get_button(
            Actions.CREATE_MESSAGE,
            ButtonsLabels.CREATE_MESSAGE,
            channel_id, channel_name),
            Buttons.get_button(
            Actions.CREATE_POST,
            ButtonsLabels.CREATE_POST,
            channel_id, channel_name)],
        [Buttons.BACK(Actions.MANAGMENT_LIST),
            Buttons.get_button(Actions.MANAGEMENT_HELP,
                               ButtonsLabels.HELP,
                               channel_id, channel_name)]
    ])


def get_need_payment_keyboard(channel_id, channel_name):
    """ Return keyboard for payment poorpose

    :param channel_id: channel id
    :type channel_id: basestring
    :param channel_name: channel name
    :type channel_name: basestring
    :return: InlineKeyboardMarkup
    :rtype: telegram.InlineKeyboardMarkup
    """
    return InlineKeyboardMarkup([
        [Buttons.BACK(Actions.MANAGMENT_LIST),
         Buttons.get_button(Actions.MANAGEMENT_HELP,
                            ButtonsLabels.HELP,
                            channel_id, channel_name)]
    ])
