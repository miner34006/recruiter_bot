# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CHANNEL_NAME_MAX_LENGTH = 30
CHANNEL_NAME_MIN_LENGTH = 5
USERNAME_MAX_LENGTH = 32
MAXIMUM_INLINE_LENGTH = 4096
CHANNEL_FULL_NAME_LENGTH = 140
INVITE_LINK_LENGTH = 60


class States(object):
    GET_MESSAGE = 'get_message'
    GET_POST_DATA = 'get_post_data'


class Actions(object):
    MANAGEMENT_HELP = 'manage_help'
    CLEAR = 'clear'
    MANAGMENT_LIST = 'manage_list'
    STATISTICS_LIST = 'stats_list'
    STOP_REFERRAL = 'stop'
    START_REFERRAL = 'start'
    CREATE_POST = 'create'
    CREATE_MESSAGE = 'setting'
    JOIN_PROGRAM = 'join'
    FULL_STATS = 'fullStats'
    DUMMY = 'dummy'


class Commands(object):
    ADD = 'add'
    STATISTICS = 'stats'
    MANAGMENT = 'manage'
    START = 'start'
    HELP = 'help'
    CANCEL = 'cancel'


class Emoji:
    LEFT_ARROW = '➡️'
    RIGHT_ARROW = '⬅️'
    INFORMATION = '📑'
    SHARE = '🗣'
    START = '👩‍👩‍👧‍👧'


class ButtonsLabels(object):
    JOIN_PROGRAM = 'Учавствовать'
    PUBLISH = 'Опубликовать'
    HELP = '❔Помощь❔'
    CREATE_MESSAGE = 'Настроить сообщение'
    BACK = '⬅️'
    CREATE_POST = 'Опубликовать пост'
    FULL_STATS = 'Полная статистика'
    STOP_REFERRAL = 'Остановить рекрутинг'
    CLEAR_STATISTICS = 'Обнулить статистику'
    START_REFERRAL = 'Возобновить рекрутинг'
    STATISCTICS = 'Статистика'
    SHOW_LINK = 'Показать ссылку'
    GO_TO = '{0} Перейти на канал {1}'.format(Emoji.LEFT_ARROW,
                                              Emoji.RIGHT_ARROW)
    CREATE_REFERRAL = 'Запустить рекрутскую программу {0}'.format(Emoji.START)
    MY_REFERALS = 'Мои программы'
    IN_REFERALS = 'Учавствую в программах'
    INFORMATION = 'Информация'
    GO_MAIN = 'На главную'
    SHARE_LINK = 'Поделиться ссылкой {0}'.format(Emoji.SHARE)
    SAVE = 'Сохранить'
    CANCEL = 'Отменить'
    PREREVIEW = 'Предпросмотр'


class Links(object):
    BASE = 'https://t.me/{0}'
    INFORMATION = 'https://t.me/recruiterInfo'
    SERVICE_LINK = 'https://t.me/{username}?start={code}'


# class Keyboards(object):
#     @staticmethod
#     def get_channel_inline_button(channel):
#         """ Function to get second inline keyboard for inline message (GO TO CHANNEL).
#         After clicking on this button, user will go to the channel.

#         :param channel: channel link to go
#         :type channel: basestring
#         :return: inline keyboard
#         :rtype: list
#         """
#         return InlineKeyboardMarkup([
#             [InlineKeyboardButton(ButtonsLabels.GO_TO, url=Links.BASE.format(channel))]
#         ])

#     GO_MAIN = InlineKeyboardButton(ButtonsLabels.GO_MAIN, callback_data='show_help')
#     MAIN = InlineKeyboardMarkup([
#         [InlineKeyboardButton(ButtonsLabels.CREATE_REFERRAL, callback_data='create_referral')],
#         [
#             InlineKeyboardButton(ButtonsLabels.MY_REFERALS, callback_data='show_referrals'),
#             InlineKeyboardButton(ButtonsLabels.STATISCTICS, callback_data='show_stats'),
#         ],
#         [InlineKeyboardButton(ButtonsLabels.INFORMATION, callback_data='show_help')]
#     ])

class Messages(object):
    POST_CREATION = '<b>Создание информационного поста</b> для канала @{0}. ' \
                    'Отправьте боту то, что хотите опубликовать. ' \
                    'Это может быть <b>текст</b> или <b>фотографии</b>.' \
                    '\n\n Для отмены используйте /cancel '
    NOTHING_TO_PUBLISH = 'Нет данных для публикации. Отправьте текстовое сообщение или картинку чтобы создать информационный пост.'
    NOTHING_TO_PREVIEW = 'Нет данных для предпросмотра. Отправьте текстовое сообщение или картинку чтобы создать информационный пост.'
    RECEIVED = 'Принято'
    CHANNEL_ALREADY_IN_DB = 'Этот канал <b>уже учавствует в рекуртской программе</b>! Попробуйте добавить другой или ' \
                            'отправьте /cancel для отмены.'
    HEADER = '<b>@{0}</b>\n\n'
    SELECT_CHANNEL_TO_MANAGE = '<b>Выберете канал</b> для управления'
    CHANNEL_ADD_SUCCESS = 'Рекрутская программа <b>успешно запущена</b> в канале @{0}. Чтобы поделиться этим с вашими подписчиками, ' \
                          '<b>выполните команду</b> /manage и опубликуйте новость в канале.\n\n' \
                          '<b>Рекрутская программа оплачена до {1}</b>, для продления - воспользуйтесь кнопкой <i>"продлить"</i> в ' \
                          'меню /manage вашего канала.'

    MANAGMENT_HELP = '<b>Доступные действия</b>:\n\n' \
                     '1. <i>Возобновить рекрутинг</i>. <b> Возобновляет рекрутскую программу в канале</b>: ' \
                     'у учатников программы появляется возможность оставлять пригласительные ссылки на ваш канал.\n\n' \
                     '2. <i>Остановить рекрутинг</i>. <b>Останавливает рекрутскую программу</b> ' \
                     'в выбранном канале: участники программы больше не имеют возможности оставлять пригласительные ' \
                     'ссылки на ваш канал через inline бота.\n\n' \
                     '3. <i>Настроить сообщение</i>. Настроить <b>шаблон сообщения, которое отправляет бот</b>, ' \
                     'когда рекрутер приглашает пользователей в ваш канал.\n\n' \
                     '4. <i>Опубликовать пост</i>. Создать сообщение, которое <b>будет опубликовано в вашем ' \
                     'канале </b>с призывом поучавствовать в рекрутской программе.\n\n'
    USER_NOT_ADMIN = 'К сожалению, у вас недостаточно прав для совершения данного действия! ' \
                     '<b>Свяжитесь с разработчиками бота!</b> '
    CANCEL_REFERRAL = 'Запуск рекрутской программы отменен'
    NOT_CHANNEL_MESSAGE = 'К сожалению, это <b>не сообщение от канала</b>.'
    NOT_IN_ADMINS_LIST = 'Кажется, вы <b>не добавили меня в администраторы вашего канала</b>. ' \
                         '\nПерешлите сообщение из своего канала как только сделаете это.'
    CHANNEL_ADD = '<b>Запуск рекрутской программы</b>\n\n' \
                'Чтобы запустить рекрутскую программу в канале, вы должны выполнить два следующих шага:\n\n' \
                '1. <b>Добавьте меня в администраторы</b> вашего канала;\n' \
                '2. Перешлите мне любое <b>сообщение из вашего канала</b>.\n\n' \
                'Для отмены выполните команду /cancel'
    MESSAGE_ADD = '@{0}\n\n' \
                  '<b>Приветственное соообщение</b> - сообщение, которое присылает бот, когда ваш рекрутер приглашает пользователей' \
                  ' в ваш канал.\n\nЧтобы создать сообщение - отправьте текст боту и нажмите кнопку <i>"Сохранить"</i>. Для отмены нажмите кнопку ' \
                  '<i>"Отменить"</i> или выполните команду /cancel\n\n<b>‼️ВАЖНО‼️</b>\n<b>Не размещайте прямые ссылки, а также @{0} в сообщении</b>!' \
                  'Ссылка на ваш канал будет прикреплена к сообщению: так мы сможем учесть дейтельность ваших рекрутеров!'
    CANCEL_MESSAGE = 'Редактирование приветственного сообщения отменено'
    CANCEL_POST_CREATION = 'Создание поста отменено'
    SAVE_MESSAGE = 'Приветственное сообщение сохранено'
    NEED_PAYMENT = '<b>Срок оплаты рекрутской программы истек</b>! Вы можете возобновиить программу, нажав на кнопку <i>"продлить"</i>'
    HELP = 'Вы моежете <b>управлять мной</b>, посылая следующие команды:\n\n' \
           '/start - начать пользоваться ботом\n' \
           '/add - добавить канал в рекрутскую программу\n' \
           '/manage - управление запущенным рекрутскими программами\n' \
           '/stats - получить статистику по запущенным рекрутским программам\n' \
           '/help - получить список команд и их описание\n\n' \
           '<b>Больше информации</b> о принципах моей работы вы можете найти, нажав на кнопку <i>"Информация"</i>.'
    SELECT_CHANNEL = '<b>Выберете канал</b> по которому хотите получить статистику'
    HELLO = 'Привет, меня зовут <b>Рекрутер</b>! Я помогу тебе организовать рекрутскую программу в твоем канале.\n\n'

    BAD_REFERRAL = 'К сожалению, данный канал <b>не учавствует в рекрутской программе или она уже завершилась</b>.'
    BAD_INVITE = 'К сожалению, данная ссылка <b>недействительна или рекрутская программа уже завершилась</b>.'

    INVITE_LINK = 'Спасибо за участие в рекрутской программе! Теперь <b>перейди в сообщество</b> - ' \
                  '<a href="https://t.me/{channel}">{channel}</a> и <b>стань его участником </b>.'
    REFERRAL_LINK = 'Спасибо что откликнулись на приглашение поучавствовть в рекрутской программе! ' \
                    'Теперь ваша задача - <b>привести как можно больше людей</b>, в канал ' \
                    '<a href="https://t.me/{0}">{0}</a>, используя свою <i>персоональную ссылку</i>. ' \
                    'Нажав на кнопку <i>"Поделиться ссылкой"</i> выберете пользователя и канал, которым вы ' \
                    'хотите поделиться.'
    NO_REFERRAL_CHANNELS = 'К сожалению, у вас нет каналов учавствующих в рекрутских программах.'
    NO_PARTICAPANTS = 'К сожалению, вы не учавствуете ни в одной рекурсткой программе! Чтобы стать рекрутером ' \
                      'канала или группы, <b>перейдите по ссылке, отправленной администратором</b> этого сообщества.'
    INLINE_MESSAGE = 'Привет! Я рекрутер из сообщества <b>{channel}</b>. Советую подписаться! ' \
                     'Чтобы показать ссылку на сообщество, нажми на кнопку <i>"Показать ссылку"</i>.'
    INLINE_LINK_APPERED = 'Теперь <b>нажмите на кнопку</b> <i>"Перейти на канал"</i>, чтобы открыть страницу сообщества!' \
                          '<a href="https://t.me/{0}">&#160;</a>'
    ALREADY_IN_REFERRAL = 'Вы уже учавствуете в рекрутской программе сообщества <a href="https://t.me/{0}">{0}</a>! ' \
                          'Используйте свою <i>персоональную ссылку</i>. Нажмите на кнопку ' \
                          '<i>"Поделиться ссылкой"</i>, выберете пользователя и канал, ' \
                          'которым вы хотите поделиться.'
    CHANNEL_HAS_NO_NAME = 'У вашего канала отсутствует @никнейм, пожалуйста перейдите в настройки канала и установите его.'
    MORE_THAN_MAXIMUM_LENGTH = 'Длина сообщения <b>превышает максимально допустимое значение</b> - 4096 символов.'
    PUBLISH_POST = 'Информационный пост опубликован'
