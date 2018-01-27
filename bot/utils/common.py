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
        '''Привет. Я SAuto для поиска , ремонта и продажи вашего автомобиля. Я свяжу вас напрямую с личным менеджером, который будет закреплён за вами после принятии, оставленной вами заявки. Менеджер полностью проконсультирует вас по любому вопросу ремонта вашего авто , продаже и поможет подобрать машину вашей мечты. В чем плюсы?

1. Машина будет соответствовать вашим деньгам, будет лучшим выбором на вторичном рынке как по цене , так и по общему состоянию. Найденный нами автомобиль будет не только лучшим, но и очень выгодным.

2. Ремонт вашего Авто будет произведено в сервисах, которые проверенные тысячами автолюбителями и являются самыми близкими к вам так же выгодными. 

3. Продажа вашего Авто не принесёт вам хлопот. Вы получите ту сумму, которую ждёте, без ваших усилили , мы сделаем все за вас.''',
        reply_markup=ReplyKeyboardMarkup(
            keyboard_start
        )
    )
    return ConversationHandler.END
