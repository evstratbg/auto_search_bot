from telegram.ext import (
    ConversationHandler, CommandHandler, MessageHandler,
    Filters, RegexHandler, Dispatcher
)
from telegram import (
    Bot, Update, ReplyKeyboardMarkup, ParseMode
)

from bot.data.states import (
    GET_QUESTION
)
from bot.data.keyboards import back, keyboard_start
from bot.utils.send_previous_msg import is_back
from bot.logger import log
from bot.bot import start


from config import ADMIN_ID


@log
def start_just_ask(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    send_params = {
        'chat_id': uid,
        'text': 'Здесь можно задать любой вопрос. '
                'На все адекватные ответим :)\n\n'
                'Этого бота написал @evstrat',
        'reply_markup': ReplyKeyboardMarkup(back, resize_keyboard=1)
    }
    user_data['previous_msg'] = send_params
    user_data['handler_type'] = 'Вопрос'
    bot.send_message(**send_params)
    return GET_QUESTION


@log
def get_question(bot: Bot, update: Update, user_data: dict) -> int:
    uid = update.message.from_user.id
    message = update.message.text
    first_name = update.message.from_user.first_name

    if is_back(message):
        bot.send_message(
            uid,
            'Предыдущее меню',
            reply_markup=ReplyKeyboardMarkup(keyboard_start)
    )

    handler_type = user_data['handler_type']

    msg = f'<b>{handler_type}</b>\n\n'
    msg += f'{message}\n'

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
    body = ConversationHandler(
        entry_points=[
            RegexHandler(
                'Задать вопрос',
                start_just_ask,
                pass_user_data=True
            ),
        ],
        states={
            GET_QUESTION: [
                MessageHandler(
                    Filters.text,
                    get_question,
                    pass_user_data=True),
    ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    dp.add_handler(body)