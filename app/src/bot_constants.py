# -*- coding: utf-8 -*-

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

CHANNEL_NAME_MAX_LENGTH = 30
CHANNEL_NAME_MIN_LENGTH = 5
USERNAME_MAX_LENGTH = 32
MAXIMUM_INLINE_LENGTH = 4096
CHANNEL_FULL_NAME_LENGTH = 140
INVITE_LINK_LENGTH = 60

PAY_WEEK = 1
PAY_MONTH = 2
PAY_ALWAYS = 3


class States(object):
    GET_MESSAGE = 'get_message'
    GET_POST_DATA = 'get_post_data'
    GET_PRICE_OPTION = 'get_price_option'


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
    START_PAYMENT = 'start_payment'
    PROCESS_PAYMENT = 'process_payment'


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
    BACK_TO_MANAGMENT = 'Вернуться к управлению каналом'
    ADD_GUIDE = 'Добавить инструкцию'
    REMOVE_GUIDE = 'Удалить инструкцию'
    JOIN_PROGRAM = 'Участвовать'
    PUBLISH = 'Опубликовать'
    HELP = '❔Помощь❔'
    CREATE_MESSAGE = 'Настроить сообщение'
    BACK = '⬅️'
    CREATE_POST = 'Опубликовать пост'
    FULL_STATS = 'Полная статистика'
    STOP_REFERRAL = 'Остановить реферальную программу'
    CLEAR_STATISTICS = 'Обнулить статистику'
    START_REFERRAL = 'Возобновить реферальную программу'
    STATISCTICS = 'Статистика'
    SHOW_LINK = 'Показать ссылку'
    GO_TO = '{0} Перейти на канал {1}'.format(Emoji.LEFT_ARROW,
                                              Emoji.RIGHT_ARROW)
    CREATE_REFERRAL = 'Запустить реферальную программу {0}'.format(Emoji.START)
    MY_REFERALS = 'Мои программы'
    IN_REFERALS = 'Участвую в программах'
    INFORMATION = 'Информация'
    GO_MAIN = 'На главную'
    SHARE_LINK = 'Поделиться ссылкой {0}'.format(Emoji.SHARE)
    SAVE = 'Сохранить'
    CANCEL = 'Отменить'
    PREREVIEW = 'Предпросмотр'
    START_PAYMENT = 'Оплатить реферальную программу'
    PAY = 'Оплатить'


class Links(object):
    BASE = 'https://t.me/{0}'
    INFORMATION = 'https://t.me/referral_tgInfo'
    SERVICE_LINK = 'https://t.me/{username}?start={code}'


class Messages(object):
    POST_IMAGE_ERROR = 'Ошибка при загрузке изображения 😟'
    POST_CREATION = '<b>Создание информационного поста</b> для канала @{0}. ' \
                    'Отправьте боту то, что хотите опубликовать. ' \
                    'Это может быть <b>текст</b> или <b>фотографии</b>.' \
                    '\n\n Для отмены используйте /cancel '
    NOTHING_TO_PUBLISH = 'Нет данных для публикации. Отправьте текстовое сообщение или картинку чтобы создать информационный пост.'
    NOTHING_TO_PREVIEW = 'Нет данных для предпросмотра. Отправьте текстовое сообщение или картинку чтобы создать информационный пост.'
    RECEIVED = 'Принято'
    CHANNEL_ALREADY_IN_DB = 'Этот канал <b>уже добавлен в систему</b>! Попробуйте добавить другой или ' \
                            'отправьте /cancel для отмены.'
    HEADER = '<b>@{0}</b>\n\n'
    SELECT_CHANNEL_TO_MANAGE = '<b>Выберете канал</b> для управления'
    CHANNEL_ADD_SUCCESS = 'Реферальная программа <b>успешно запущена</b> в канале @{0}. Чтобы поделиться этим с вашими подписчиками, ' \
                          '<b>выполните команду</b> /manage и опубликуйте новость в канале.\n\n' \
                          '<b>Реферальная программа оплачена до {1}</b>, для продления - воспользуйтесь кнопкой <i>"Оплатить реферальную программу"</i> в ' \
                          'меню /manage вашего канала.'
    SELECT_PAYMENT_OPTION = 'Для <b>продления реферальной программы</b>, выберете одну из следующих опций'
    MANAGMENT_HELP = '<b>Доступные действия</b>:\n\n' \
                     '1. <i>Оплатить реферальную программу</i>.  <b>Продлить реферальную программу </b> на срок неделя/месяц/бессрочно ' \
                     '(по истечении срока подписки на бота, реферальная программа автоматически останавливается).\n\n' \
                     '2. <i>Возобновить реферальную программу</i>. <b> Возобновление реферальной программы в канале</b> - ' \
                     'у рекрутеров появляется возможность оставлять пригласительные ссылки на ваш канал.\n\n' \
                     '3. <i>Остановить реферальную программу</i>. <b>Остановка реферальной программы</b> ' \
                     'в выбранном канале - рекрутеры больше не имеют возможности оставлять пригласительные ' \
                     'ссылки на ваш канал.\n\n' \
                     '4. <i>Настроить сообщение</i>. Настройка <b>шаблона сообщения, которое отправляет бот</b>, ' \
                     'когда рекрутер приглашает пользователей в ваш канал.\n\n' \
                     '5. <i>Опубликовать пост</i>. Создание поста, который <b>будет опубликован в вашем ' \
                     'канале </b>с призывом поучаствовать в реферальной программе и кнопкой для регистрации рекрутеров..\n\n'
    USER_NOT_ADMIN = 'К сожалению, у вас недостаточно прав для совершения данного действия! ' \
                     '<b>Свяжитесь с разработчиками бота!</b> '
    CANCEL_REFERRAL = 'Запуск реферальной программы отменен'
    NOT_CHANNEL_MESSAGE = 'К сожалению, это <b>не сообщение от канала</b>.'
    NOT_IN_ADMINS_LIST = 'Кажется, вы <b>не добавили меня в администраторы вашего канала</b>. ' \
                         '\nПерешлите сообщение из своего канала как только сделаете это.'
    CHANNEL_ADD = '<b>Запуск реферальной программы</b>\n\n' \
                'Чтобы запустить реферальную программу в канале, вы должны выполнить два следующих шага:\n\n' \
                '1. <b>Добавьте меня в администраторы</b> вашего канала;\n' \
                '2. Перешлите мне любое <b>сообщение из вашего канала</b>.\n\n' \
                'Для отмены выполните команду /cancel'
    MESSAGE_ADD = '@{0}\n\n' \
                  '<b>Приветственное соообщение</b> - сообщение, которое присылает бот, когда ваш рекрутер приглашает пользователей' \
                  ' в ваш канал.\n\nЧтобы создать сообщение - отправьте текст боту и нажмите кнопку <i>"Сохранить"</i>. Для отмены нажмите кнопку ' \
                  '<i>"Отменить"</i> или выполните команду /cancel\n\n<b>‼️ВАЖНО‼️</b>\n<b>Не размещайте прямые ссылки, а также @{0} в сообщении</b>!' \
                  ' Ссылка на ваш канал будет прикреплена к сообщению: так, мы сможем учесть дейтельность ваших рекрутеров!'
    CANCEL_MESSAGE = 'Редактирование приветственного сообщения отменено'
    CANCEL_POST_CREATION = 'Создание поста отменено'
    SAVE_MESSAGE = 'Приветственное сообщение сохранено'
    POST_GUIDE = 'Чтобы стать рекрутером, нажмите на кнопку <i>"Участвовать"</i>. ' \
                 ' Чтобы пригласить пользователя, наберите @referral_tgBot в любом диалоге и выберете канал ' \
                 '<b>{0}</b>, чтобы порекомендовать его.'
    NEED_PAYMENT = '<b>Срок оплаты реферальной программы истек</b>! Вы можете возобновиить ' \
                   'программу, нажав на кнопку <i>"Продлить"</i>'
    HELP = 'Вы можете <b>управлять мной</b>, посылая следующие команды:\n\n' \
           '/start - начать пользоваться ботом\n' \
           '/add - запустить реферальную программу в канале\n' \
           '/manage - управление запущеннымм реферальнымм программами\n' \
           '/stats - получить статистику по запущенным реферальным программам\n' \
           '/help - получить список команд и их описание\n\n' \
           '<b>Больше информации</b> о принципах моей работы вы можете найти, нажав на кнопку <i>"Информация"</i>.'
    SELECT_CHANNEL = '<b>Выберете канал</b> по которому хотите получить статистику'
    HELLO = 'Привет, меня зовут <b>Referral bot</b>! Я помогу тебе организовать реферальную программу в твоем канале.\n\n'
    ON_UPGRADE = 'В данный момент проводятся <b>технические работы</b>. ' \
                 'Приносим свои извинения.'
    BAD_REFERRAL = 'К сожалению, данный канал <b>не участвует в реферальной программе или она уже завершилась</b>.'
    BAD_INVITE = 'К сожалению, данная ссылка <b>недействительна или реферальная программа уже завершилась</b>.'

    INVITE_LINK = 'Спасибо за участие в реферальной программе! Теперь <b>перейди в сообщество</b> - ' \
                  '<a href="https://t.me/{channel}">{channel}</a> и <b>стань его участником </b>.'
    REFERRAL_LINK = 'Спасибо что откликнулись на приглашение поучаствовать в реферальной программе! ' \
                    'Теперь ваша задача - <b>привести как можно больше людей</b>, в канал ' \
                    '<a href="https://t.me/{0}">{0}</a>, используя свою <i>персоональную ссылку</i>. ' \
                    'Нажав на кнопку <i>"Поделиться ссылкой"</i> выберете пользователя и канал, которым вы ' \
                    'хотите поделиться.'
    NO_REFERRAL_CHANNELS = 'К сожалению, у вас нет каналов в которых запущены реферальные программы.'
    NO_PARTICAPANTS = 'К сожалению, вы не участвуете ни в одной реферальной программе! Чтобы стать рекрутером ' \
                      'канала или группы, <b>перейдите по ссылке, отправленной администратором</b> этого сообщества.'
    INLINE_MESSAGE = 'Привет! Я рекрутер из сообщества <b>{channel}</b>. Советую подписаться! '
    INLINE_GUIDE = '\n\nЧтобы получить ссылку на сообщество, нажмите на кнопку <i>"Показать ссылку"</i>.'

    PUSH_BUTTON_TO_PAY = '<b>Нажмите на кнопку</b> <i>оплатить</i>, чтобы перейти на страницу оплаты'
    INLINE_LINK_APPERED = 'Теперь <b>нажмите на кнопку</b> <i>"Перейти на канал"</i>, чтобы открыть страницу сообщества!' \
                          '<a href="https://t.me/{0}">&#160;</a>'
    ALREADY_IN_REFERRAL = 'Вы уже участвуете в реферальной программе сообщества <a href="https://t.me/{0}">{0}</a>! ' \
                          'Используйте свою <i>персоональную ссылку</i>. Нажмите на кнопку ' \
                          '<i>"Поделиться ссылкой"</i>, выберете пользователя и канал, ' \
                          'которым вы хотите поделиться.'
    CHANNEL_HAS_NO_NAME = 'У вашего канала отсутствует @никнейм, пожалуйста перейдите в настройки канала и установите его.'
    MORE_THAN_MAXIMUM_LENGTH = 'Длина сообщения <b>превышает максимально допустимое значение</b> - 4096 символов.'
    PUBLISH_POST = 'Информационный пост опубликован'
    NEED_ADMIN = 'Похоже, вы удалили меня из администраторов канала @{0}. ' \
                 '<b>Добавьте меня в администраторы</b> и попробуйте еще раз.'
                 
    ERROR = 'Произошла неизвестная ошибка 🤕, мы уже работаем над ней.\n' \
            '<b>Пожалуйста, сообщите о данной проблеме разработчикам бота - @miner34006!</b>'
    TOO_MANY_MEMBERS = 'В вашем канале слишком много подписчиков! ' \
                       '<b>Пожалуйста, свяжитесь с разработчиками бота </b> - @miner34006 для уточнения деталей платежа.'
