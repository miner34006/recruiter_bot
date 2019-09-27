# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timedelta

from app.src.bot_constants import *
from app.src.utils import *
from . import db, db_session

logger = logging.getLogger()


class Channel(db.Model):
    __tablename__ = 'channels'
    __table_args__ = {'extend_existing': True}

    channel_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(CHANNEL_FULL_NAME_LENGTH),
                     nullable=False)
    username = db.Column(db.String(CHANNEL_NAME_MAX_LENGTH), nullable=False,
                         unique=True)
    admin = db.Column(db.String(USERNAME_MAX_LENGTH), nullable=False)
    message = db.Column(db.Text)
    is_running = db.Column(db.Boolean, default=True)
    due_date = db.Column(db.DateTime, nullable=True)
    has_infinite_subsribe = db.Column(db.Boolean, default=False)

    inviters = db.relationship('ChannelInviter', back_populates="channel")
    receivers = db.relationship('Referral', back_populates='channel')

    def __init__(self, channel_id, username, name, admin=None,
                 message=None, due_date=None):
        self.channel_id = channel_id
        self.username = username
        self.name = name
        self.admin = admin
        self.message = message or Messages.INLINE_MESSAGE.format(channel=name)
        self.due_date = due_date or datetime.today() + timedelta(days=1)

    def __repr__(self):
        return '<Channel {0}>'.format(self.name)

    @classmethod
    def exists_in_db(cls, channel_id):
        q = db_session.query(Channel.channel_id) \
            .filter(Channel.channel_id == channel_id)
        return db_session.query(q.exists()).scalar()


class Inviter(db.Model):
    __tablename__ = 'inviters'
    __table_args__ = {'extend_existing': True}

    inviter_id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(USERNAME_MAX_LENGTH), unique=True,
                     nullable=False)

    channels = db.relationship('ChannelInviter', back_populates="inviter")
    receivers = db.relationship('Referral', back_populates='inviter')

    def __init__(self, inviter_id, name):
        self.inviter_id = inviter_id
        self.name = name

    def __repr__(self):
        return '<Inviter {0}>'.format(self.name)


class ChannelInviter(db.Model):
    __tablename__ = 'channelInviters'
    __table_args__ = {'extend_existing': True}

    inviter_id = db.Column(db.BigInteger, db.ForeignKey('inviters.inviter_id'),
                           primary_key=True)
    channel_id = db.Column(db.BigInteger,  db.ForeignKey('channels.channel_id'),
                           primary_key=True)
    code = db.Column(db.String(INVITE_LINK_LENGTH), primary_key=True,
                     unique=True)

    inviter = db.relationship(Inviter, back_populates="channels")
    channel = db.relationship(Channel, back_populates="inviters")

    def __init__(self, inviter_id, channel_id, code=None):
        self.inviter_id = inviter_id
        self.channel_id = channel_id
        self.code = get_referral_unique_code()

    def __repr__(self):
        return '<Inviter {0} from channel {1}>'.format(self.inviter_id,
                                                       self.channel_id)


class Referral(db.Model):
    __tablename__ = 'referrals'
    __table_args__ = {'extend_existing': True}

    inviter_id = db.Column(db.BigInteger,
                           db.ForeignKey('inviters.inviter_id'),
                           nullable=False)
    channel_id = db.Column(db.BigInteger,
                           db.ForeignKey('channels.channel_id'),
                           primary_key=True)
    receiver_id = db.Column(db.BigInteger, primary_key=True)

    inviter = db.relationship(Inviter, back_populates="receivers")
    channel = db.relationship(Channel, back_populates="receivers")

    def __init__(self, inviter_id, channel_id, receiver_id):
        self.inviter_id = inviter_id
        self.channel_id = channel_id
        self.receiver_id = receiver_id

    def __repr__(self):
        return '<Referral: {0} invite {1} to {2}>'.format(
            self.inviter_id, self.receiver_id, self.channel_id)

    @classmethod
    def get_new_users(cls, bot, channel_id):
        """ Get new users from referral program

        :param bot: bot object
        :type bot: telegram.Bot
        :param channel_id: id of the channel
        :type channel_id: int
        """
        new_users = db_session.query(Referral.receiver_id).filter_by(
            channel_id=channel_id).all()
        for user_id in new_users:
            if not user_in_channel(bot, user_id[0], channel_id):
                logger.debug('<user:{0}> not in <channel:{1}>'
                              .format(user_id, channel_id))
                new_users.remove(user_id)
        return [user[0] for user in new_users]
