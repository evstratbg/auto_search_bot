from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    Filters, RegexHandler, Dispatcher
)
from telegram import (
    Bot, Update, ReplyKeyboardMarkup, ParseMode, KeyboardButton
)

from bot.data.states import (
    GET_CAR_BRAND, GET_YEAR, GET_PHONE_NUMBER, GET_PROBLEM
)
from bot.data.keyboards import back, keyboard_start
from bot.utils.send_previous_msg import is_back
from bot.logger import log
from bot.bot import start
from bot.auto.search import (
    get_estimated_amount, get_auto_brand, get_year
)



@log
def start_presale(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    send_params = {
        'chat_id': uid,
        'text': 'Продиагностируем всемэлектрические системы автомобиля и '
                'выявим неисправности. Плюс в том, что к вам приедут и не '
                'придется доламывать вашу машину, по пути в сервиса.\n'
                'Напишите марку автомобиля',
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['previous_msg'] = send_params
    user_data['handler_type'] = 'Выездная диагностика'
    bot.send_message(**send_params)
    return GET_CAR_BRAND


@log
def get_problem(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    message = update.message.text
    if is_back(message):
        bot.send_message(**user_data['send_params_get_year'])
        return GET_YEAR

    user_data['problem'] = message

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


@log
def get_phone_number(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    first_name = update.message.from_user.first_name

    contact = update.message.contact

    year = user_data['year']
    brand = user_data['brand']
    handler_type = user_data['handler_type']
    problem = user_data['problem']

    msg = f'<b>{handler_type}</b>\n\n'
    msg += f'<b>Марка:</b> {brand}\n'
    msg += f'<b>Год:</b> {year}\n'
    msg += f'<b>Проблема:</b> {problem}\n\n'

    msg += f'Заказчик: <a href="tg://user?id={uid}">{first_name}</a>\n'

    bot.send_message(
        -293221983,
        msg,
        parse_mode=ParseMode.HTML
    )
    bot.send_contact(-293221983, **contact.to_dict())
    bot.send_message(
        uid,
        'Передал!',
        reply_markup=ReplyKeyboardMarkup(keyboard_start)
    )
    del user_data
    return ConversationHandler.END


def register(dp: Dispatcher):
    body = ConversationHandler(
        entry_points=[
            RegexHandler(
                'Предпродажная подготовка',
                start_presale,
                pass_user_data=True
            ),
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
            GET_PROBLEM: [
                MessageHandler(
                    Filters.text,
                    get_problem,
                    pass_user_data=True
                ),

    ],
            GET_PHONE_NUMBER: [
                MessageHandler(
                    Filters.contact,
                    get_phone_number,
                    pass_user_data=True
                )
            ]

        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(body)