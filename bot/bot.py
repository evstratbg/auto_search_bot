import logging
from telegram.ext import CommandHandler, Updater

from bot.utils.common import start
from bot.auto import search, body_work, presale, checking


def run(logger_level, workers, bot):
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logger_level
    )
    updater = Updater(workers=workers, bot=bot)
    dp = updater.dispatcher

    search.register(dp)
    body_work.register(dp)
    presale.register(dp)
    checking.register(dp)

    dp.add_handler(CommandHandler('start', start))
    updater.start_polling()
    updater.idle()
