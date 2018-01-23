from telegram import Bot
from telegram.ext import messagequeue as mq
from argparse import ArgumentParser, Namespace
import logging

from config import TOKENS, LOGGING_LEVELS
from bot import bot


class MQBot(Bot):
    '''A subclass of Bot which delegates send method handling to MQ'''
    def __init__(self, *args, is_queued_def=True, mqueue=None, **kwargs):
        super(MQBot, self).__init__(*args, **kwargs)
        # below 2 attributes should be provided for decorator usage
        self._is_messages_queued_default = is_queued_def
        self._msg_queue = mqueue or mq.MessageQueue()

    def __del__(self):
        try:
            self._msg_queue.stop()
        except:
            pass
        super(MQBot, self).__del__()

    @mq.queuedmessage
    def send_message(self, *args, **kwargs):
        '''Wrapped method would accept new `queued` and `isgroup`
        OPTIONAL arguments'''
        super(MQBot, self).send_message(*args, **kwargs)


def parse_argv() -> Namespace:
    parser = ArgumentParser(description='Starts ASB')
    parser.add_argument(
        '--token_type', '-t',
        type=str,
        default='TEST',
        help='api token name (from config) for access to bot'
    )
    parser.add_argument(
        '--workers', '-w',
        type=int,
        default=10,
        help='number of workers for running bot'
    )
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_argv()
    token_type = args.token_type.upper()
    token = TOKENS.get(token_type, TOKENS['TEST'])
    logger_level = LOGGING_LEVELS.get(token_type, logging.INFO)

    q = mq.MessageQueue(all_burst_limit=3, all_time_limit_ms=3000)
    mqbot = MQBot(token, mqueue=q)

    startup_params = {
        'logger_level': logger_level,
        'workers': args.workers,
        'bot': mqbot
    }

    bot.run(**startup_params)
