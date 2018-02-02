from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    Filters, RegexHandler, Dispatcher
)
from telegram import (
    Bot, Update, ReplyKeyboardMarkup, ParseMode, KeyboardButton
)

from bot.data.states import (
    GET_CAR_BRAND, GET_YEAR, GET_ESTIMATED_AMOUNT, GET_OTHER_WISHES,
    GET_PHONE_NUMBER, GET_PROBLEM
)
from bot.data.keyboards import back, keyboard_start
from bot.utils.send_previous_msg import is_back
from bot.logger import log
from bot.bot import start

from config import ADMIN_ID


@log
def start_search_auto(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    send_params = {
        'chat_id': uid,
        'text': 'Поможем найти машину, которая полностью '
                'будет соответствовать вашим требованиям и будет лучшей из тех, '
                'что есть на вторичном рынке. Проанализируем весь вторичный рынок, '
                'проверим автомобиль по всем базам '
                'и даже договоримся с продавцом. В связи с этим, автомобиль '
                'будет и выгодным, и надеждным.\n\n'
                'Напишите желаемую марку автомобиля',
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['previous_msg'] = send_params
    user_data['handler_type'] = 'Поиск авто'
    bot.send_message(**send_params)
    return GET_CAR_BRAND


@log
def start_match_auto(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    send_params = {
        'chat_id': uid,
        'text': 'Подберем машину, которая полностью '
                'будет соответствовать вашим требованиям, будет лучшим из тех, '
                'что есть на вторичном рынке. Данный выбор полезен тем, что мы '
                'проанализируем весь вторичный рынок, проверим автомобиль по '
                'всем базам и даже договоримся с продавцом. Приедем на место '
                'осмотра, проведем все мероприятия по выявлению неисправностей,'
                ' проверим на наличие дтп, наличие полного пакета документов, '
                'отсутствие окрашенных деталей и кузовных дефектов, ускорим '
                'оформление авто.\n\n'
                'Напишите желаемую марку автомобиля',
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['previous_msg'] = send_params
    user_data['handler_type'] = 'Подбор авто'
    bot.send_message(**send_params)
    return GET_CAR_BRAND


@log
def get_auto_brand(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    message = update.message.text
    if is_back(message):
        return start(bot, update)
    user_data['brand'] = message

    send_params = {
        'chat_id': uid,
        'text': 'Отлично! Теперь укажите год',
        'parse_mode': ParseMode.HTML,
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['send_params_get_year'] = send_params
    bot.send_message(**send_params)
    return GET_YEAR


@log
def get_year(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    message = update.message.text
    if is_back(message):
        bot.send_message(**user_data['previous_msg'])
        return GET_CAR_BRAND

    if user_data['handler_type'] == 'Выездная диагностика':
        send_params = {
            'chat_id': uid,
            'text': 'Опишите проблему максимально подробно',
            'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
        }
        user_data['send_params_problems'] = send_params
        bot.send_message(**send_params)
        return GET_PROBLEM

    user_data['year'] = message
    send_params = {
        'chat_id': uid,
        'text': 'На какую сумму рассчитываете?',
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['send_params_get_estimated_amount'] = send_params
    bot.send_message(**send_params)
    return GET_ESTIMATED_AMOUNT


@log
def get_estimated_amount(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    message = update.message.text
    if is_back(message):
        bot.send_message(**user_data['send_params_get_year'])
        return GET_YEAR
    user_data['esimated_amount'] = message
    if user_data['handler_type'] == 'Кузовной ремонт':
        send_params = {
            'chat_id': uid,
            'text': 'Отправьте свой номер телефона, чтобы мы с вами связались',
            'parse_mode': ParseMode.HTML,
            'reply_markup': ReplyKeyboardMarkup([
                [KeyboardButton('Отправить телефон', request_contact=True)]
            ],
                resize_keyboard=1
            )
        }
        bot.send_message(**send_params)
        return GET_PHONE_NUMBER

    send_params = {
        'chat_id': uid,
        'text': 'Здесь можете написать иные пожелания',
        'reply_markup': ReplyKeyboardMarkup(
            [['Пожеланий нет']] + back,
            resize_keyboard=1
        )
    }
    user_data['previous_msg'] = send_params
    bot.send_message(**send_params)
    return GET_OTHER_WISHES


@log
def get_other_wishes(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    first_name = update.message.from_user.first_name
    message = update.message.text
    if is_back(message):
        bot.send_message(**user_data['send_params_get_estimated_amount'])
        return GET_ESTIMATED_AMOUNT

    brand = user_data['brand']
    year = user_data['year']
    esimated_amount = user_data['esimated_amount']

    handler_type = user_data['handler_type']

    msg = f'<b>{handler_type}</b>\n\n'
    msg += f'<b>Марка:</b> {brand}\n'
    msg += f'<b>Год:</b> {year}\n'
    msg += f'<b>Примерная цена:</b> {esimated_amount}\n\n'

    if message != 'Пожеланий нет':
        msg += f'<b>Пожелания:</b> {message}\n\n'

    msg += f'Заказчик: <a href="tg://user?id={uid}">{first_name}</a>\n'

    bot.send_message(
        ADMIN_ID,
        msg,
        parse_mode=ParseMode.HTML
    )
    bot.send_message(
        uid,
        'Передал!',
        reply_markup=ReplyKeyboardMarkup(keyboard_start)
    )
    del user_data
    return ConversationHandler.END


def register(dp: Dispatcher):
    auto_search = ConversationHandler(
        entry_points=[
            RegexHandler('Поиск авто', start_search_auto, pass_user_data=True),
            RegexHandler('Подбор авто', start_match_auto, pass_user_data=True)
        ],
        states={
            GET_CAR_BRAND: [
                MessageHandler(
                    Filters.text,
                    get_auto_brand,
                    pass_user_data=True),
            ],
            GET_YEAR: [
                MessageHandler(
                    Filters.text,
                    get_year,
                    pass_user_data=True),
            ],
            GET_ESTIMATED_AMOUNT: [
                MessageHandler(
                    Filters.text,
                    get_estimated_amount,
                    pass_user_data=True),
            ],
            GET_OTHER_WISHES: [
                MessageHandler(
                    Filters.text,
                    get_other_wishes,
                    pass_user_data=True),
            ],

        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(auto_search)
