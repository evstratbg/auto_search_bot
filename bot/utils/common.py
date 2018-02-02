from telegram import Bot, Update, ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

from models import Users
from bot.logger import log
from bot.data.keyboards import keyboard_start


@log
def start(bot: Bot, update: Update):
    uid = update.message.from_user.id
    first_name = update.message.from_user.first_name
    username = update.message.from_user.username
    last_name = update.message.from_user.last_name

    user, created = Users.get_or_create(telegram_id=uid)
    user.first_name = first_name
    user.last_name = last_name
    user.username = username
    user.save()

    bot.send_message(
        uid,
        '''Привет. Я SAuto для поиска, ремонта и продажи вашего автомобиля. Я свяжу вас напрямую с личным менеджером, который будет закреплён за вами после принятии, оставленной вами заявки. Менеджер полностью проконсультирует вас по любому вопросу ремонта вашего авто, продаже и поможет подобрать машину вашей мечты.''',
        reply_markup=ReplyKeyboardMarkup(
            keyboard_start
        )
    )
    return ConversationHandler.END
