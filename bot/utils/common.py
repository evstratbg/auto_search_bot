from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from bot.models import Users
from bot.logger import log
from bot.data.keyboards import keyboard_start


@log
def start(bot: Bot, update: Update):
    uid = update.message.from_user.id
    first_name = update.message.from_user.first_name
    username = update.message.from_user.username
    last_name = update.message.from_user.last_name
    Users.get_or_create(
        telegram_id=uid,
        first_name=first_name,
        last_name=last_name,
        username=username
    )
    bot.send_message(
        uid,
        'Привет! Чем тебе помочь?',
        reply_markup=ReplyKeyboardMarkup(
            keyboard_start
        )
    )
    return ConversationHandler.END