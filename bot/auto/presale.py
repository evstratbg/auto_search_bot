from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    Filters, RegexHandler, Dispatcher
)
from telegram import (
    Bot, Update, ReplyKeyboardMarkup, ParseMode, KeyboardButton
)

from bot.data.states import (
    GET_CAR_BRAND, GET_YEAR, GET_PHONE_NUMBER, GET_ESTIMATED_AMOUNT
)
from bot.data.keyboards import back, keyboard_start
from bot.utils.send_previous_msg import is_back
from bot.logger import log
from bot.bot import start
from bot.auto.search import (
    get_estimated_amount, get_auto_brand, get_year
)

from config import ADMIN_ID


@log
def start_presale(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    send_params = {
        'chat_id': uid,
        'text': 'Подготовим вашу машину к продаже, дополним недостоющие '
                'элементы, отремонтируем грубые неисправности, исправим то, '
                'на что часто обращают внимание при покупке авто, чтобы вам не '
                'пришлось краснеть и скидывать сумму. '
                'При желании, поможем с продажей\n'
                'Напишите марку автомобиля',
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['previous_msg'] = send_params
    user_data['handler_type'] = 'Предпрожадная подготовка'
    bot.send_message(**send_params)
    return GET_CAR_BRAND


@log
def get_phone_number(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    first_name = update.message.from_user.first_name

    contact = update.message.contact

    year = user_data['year']
    brand = user_data['brand']
    handler_type = user_data['handler_type']
    esimated_amount = user_data['esimated_amount']

    msg = f'<b>{handler_type}</b>\n\n'
    msg += f'<b>Марка:</b> {brand}\n'
    msg += f'<b>Год:</b> {year}\n'
    msg += f'<b>Примерная цена:</b> {esimated_amount}\n\n'

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
            GET_ESTIMATED_AMOUNT: [
                MessageHandler(
                    Filters.text,
                    get_estimated_amount,
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