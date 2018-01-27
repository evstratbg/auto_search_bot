from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    Filters, RegexHandler, Dispatcher
)
from telegram import (
    Bot, Update, ReplyKeyboardMarkup, ParseMode, KeyboardButton
)

from bot.data.states import (
    GET_CAR_BRAND, GET_REPAIR_DESCRIPTION, GET_PHONE_NUMBER
)
from bot.data.keyboards import back, keyboard_start
from bot.utils.send_previous_msg import is_back
from bot.logger import log
from bot.bot import start

from config import ADMIN_ID


@log
def start_body_work(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    send_params = {
        'chat_id': uid,
        'text': 'Оставьте заявку на ремонт вашего автомобиля, '
                'либо отдельных деталей. Поможем найти и довезти '
                'детали и материалы\nВведите марку автомобиля',
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['previous_msg'] = send_params
    user_data['handler_type'] = 'Кузовной ремонт'
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
        'text': 'Отлично! Что нужно починить?',
        'parse_mode': ParseMode.HTML,
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['get_auto_brand'] = send_params
    bot.send_message(**send_params)
    return GET_REPAIR_DESCRIPTION


@log
def get_repair_description(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    message = update.message.text
    if is_back(message):
        bot.send_message(**user_data['previous_msg'])
        return GET_CAR_BRAND

    user_data['what_to_repair'] = message

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
    user_data['get_auto_brand'] = send_params
    bot.send_message(**send_params)
    return GET_PHONE_NUMBER


@log
def get_phone_number(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    first_name = update.message.from_user.first_name

    contact = update.message.contact

    what_to_repair = user_data['year']
    brand = user_data['brand']
    handler_type = user_data['handler_type']

    msg = f'<b>{handler_type}</b>\n\n'
    msg += f'<b>Марка:</b> {brand}\n'
    msg += f'<b>Что чинить:</b> {what_to_repair}\n'

    msg += f'Заказчик: <a href="tg://user?id={uid}">{first_name}</a>\n'

    bot.send_message(
        ADMIN_ID,
        msg,
        parse_mode=ParseMode.HTML
    )
    bot.send_contact(ADMIN_ID, **contact.to_dict())

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
                'Кузовной ремонт',
                start_body_work,
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
            GET_REPAIR_DESCRIPTION: [
                MessageHandler(
                    Filters.text,
                    get_repair_description,
                    pass_user_data=True),
    ],
            GET_PHONE_NUMBER: [
                MessageHandler(
                    Filters.contact,
                    get_phone_number,
                    pass_user_data=True
                )
    ],

        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(body)