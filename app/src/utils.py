# -*- coding: utf-8 -*-

import os
import random
import string
import logging

import requests
from telegram.error import BadRequest
from telegram import ParseMode, InlineKeyboardMarkup

from app.src.bot_constants import *
from app import IMAGE_CONTROLLER_PORT, IMAGE_CONTROLLER_IP

logger = logging.getLogger()


def admin_required(function):
    """ Verify bot in channel admins
    
    :param function: function to decorate
    :type function: function
    """
    def wrapper(bot, update, *args, **kwargs):
        splitted = update.callback_query.data.split(':')
        channel_id = splitted[1]
        channel_name = splitted[2]
        try:
            bot.get_chat_administrators(channel_id)
        except Exception as err:
            bot.send_message(
                chat_id=update.effective_chat.id,
                parse_mode=ParseMode.HTML,
                text=Messages.NEED_ADMIN.format(channel_name))
            return None
            
        return function(bot, update, *args, **kwargs)
    return wrapper


class Buttons(object):
    """ Bot buttons
    """
    @staticmethod
    def get_button(action, label, channel_id, channel_name, *additional):
        """ Get button according to labels, actions and channel creds

        :param action: button action
        :type action: basestring
        :param label: button's label
        :type label: basestring
        :param channel_id: channel id
        :type channel_id: int
        :param channel_name: channel name
        :type channel_name: basestring
        :param additional: additional fields
        :type additional: list with str
        :return: button object
        :rtype: InlineKeyboardButton
        """
        additional_fields = ''
        for field in additional:
            additional_fields += ':{0}'.format(field)
        return InlineKeyboardButton(label, callback_data='{0}:{1}:{2}{3}'
                                    .format(action, 
                                            channel_id, 
                                            channel_name, 
                                            additional_fields))

    # Back to channel list button
    BACK = staticmethod(
        lambda back: InlineKeyboardButton(ButtonsLabels.BACK,
                                          callback_data=back))

    # Link to information channel
    INFORMATION = InlineKeyboardButton(ButtonsLabels.INFORMATION,
                                       url=Links.INFORMATION)


def send_response(bot, update, new_text, reply_markup=None,
                  parse_mode=ParseMode.HTML):
    """ Function to reponse for user actions: new message or query

    :param bot: bot object
    :type bot: telegram.Bot
    :param update: incomming update
    :type update: telegram.Update
    :param new_text: new text for user
    :type new_text: basestring
    :param reply_markup: reply_markup, defaults to None
    :type reply_markup: reply_markup, optional
    :param parse_mode: parse mode, defaults to ParseMode.HTML
    :type parse_mode: ParseMode.HTML
    :return: None
    """
    logger.debug('Sending/editting message with text <{0}>, reply_markup <{1}>'.format(new_text, reply_markup))
    if update.message:
        bot.send_message(
            chat_id=update.effective_chat.id,
            parse_mode=parse_mode,
            text=new_text,
            reply_markup=reply_markup)

    elif update.callback_query:
        try:
            bot.edit_message_text(
                chat_id=update.effective_chat.id,
                text=new_text,
                message_id=update.effective_message.message_id,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except BadRequest as err:
            logging.error('Failed to send/edit message. Reason: {0}.'.format(err))
        update.callback_query.answer()


def get_referral_unique_code(length=INVITE_LINK_LENGTH):
    """ Function to get referral unique code with length from parameter

    :param length: code length, defaults to bot_constants.INVITE_LINK_LENGTH
    :type length: basestring, optional
    :return: unique code
    :rtype: basestring
    """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for _ in range(length))


def create_inline_keyboard(buttons, width=1):
    """ Create keyboard from list of buttons

    :param buttons: buttons for keyboard
    :type buttons: list
    :param width: keyboard width, defaults to 1
    :type width: int, optional
    :return: created keyboard
    :rtype: InlineKeyboardMarkup
    """
    keyboard = []
    row = []
    for button in buttons:
        row.append(button)
        if len(row) == width:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)


def user_in_channel(bot, user_id, channel_id):
    """ Checks that user is in the channel

    :param user_id: telegram user id
    :type user_id: int
    :param channel_id: telegram channel id
    :type channel_id: int
    """
    try:
        return bot.get_chat_member(channel_id, user_id).status != 'left'
    except Exception as err:
        logger.warning('exception while getting <user:{0}> from <chat:{1}>, '
                       'reason: {2}'.format(user_id, channel_id, err))
        return False


def get_channel_logo(bot, channel_id):
    """ Getting channel logo from telegram

    :param bot: bot object
    :type bot: telegram.Bot
    :param channel_id: channel id to get logo from
    :type channel_id: basestring
    :return: url do download image if success, None o.w.
    :rtype: basestring
    """
    chat = bot.get_chat(channel_id)
    if chat.photo:
        file_id = chat.photo.big_file_id
        file = bot.get_file(file_id)
        return file.file_path

    logger.warning('Failed to get logo url for channel {0}'.format(channel_id))
    return None


def download_image(image_url, image_id, image_tag=None):
    """ Download post image to image controller

    :param image_url: url of the image to download
    :type image_url: basestring
    :param image_id: file id -> name on image controller
    :type image_id: basestring
    :param image_tag: file tag
    :type image_tag: basestring
    :return: url to image
    :rtype: str
    """
    payload = {'image_url': image_url, 'image_id': image_id}
    if image_tag:
        payload.update({'image_tag': image_tag})

    logger.debug('Downloading image with props {0}'.format(payload))
    post_url = 'http://{0}:{1}/image'.format(IMAGE_CONTROLLER_IP,
                                             IMAGE_CONTROLLER_PORT)
    try:
        response = requests.post(post_url, json=payload)
    except Exception as err:
        logger.error('Failed POSTing to controller, reason: {0}'.format(err))
        return None

    logger.debug('Response from image controller: {0}'.format(response.text))
    return response.json()['url']


def get_image_url(image_id, image_tag):
    """ Get image url from controller

    :param image_id: file id -> name on image controller
    :type image_id: basestring
    :param image_tag: file tag
    :type image_tag: basestring
    :return: url to image
    :rtype: str
    """
    url = 'http://{0}:{1}/image/{2}/{3}'.format(IMAGE_CONTROLLER_IP,
                                                IMAGE_CONTROLLER_PORT,
                                                image_tag, image_id)
    try:
        reponse = requests.get(url)
    except Exception as err:
        logger.error('Failed GETing image from controller, reason: {0}'
                     .format(err))
        return None
    logger.debug('Response from image controller {0}'.format(reponse.json()))
    return reponse.json()['url']
