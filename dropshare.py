#!/usr/bin/env python
"""
Simple Bot to upload user images to s3.

Usage:
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import logging
import random
import string
import boto3

from datetime import date
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

# Create an S3 client
s3 = boto3.client('s3')


def start(bot, update):
    """Send a message when the command /start is issued."""
    bot.send_message(chat_id=update.message.chat_id,
                     text='Hello, you can send photos and I will give the link for share.')


def document_uploader(bot, update):
    """Send a message when the user send document"""
    bot.send_message(chat_id=update.message.chat_id,
                     text='Please send only photos.')


def photo_uploader(bot, update):
    """Uploads user's image."""
    bucket_name = 'drop-and-share'
    domain = bucket_name + '.s3.eu-central-1.amazonaws.com'

    photo_file = update.message.photo[-1].get_file()
    photo_name = get_random_name(6)
    day_elapsed = (date(2019, 6, 14) - date.today()).days + 1000

    local_file = '/tmp/' + photo_name + '.jpg'
    remote_file = str(day_elapsed) + '/' + photo_name + '.jpg'

    photo_file.download(local_file)
    s3.upload_file(local_file, bucket_name, remote_file,
                   ExtraArgs={'ContentType': "image/jpeg", 'ACL': "public-read"})

    bot.send_message(chat_id=update.message.chat_id,
                     text="https://" + domain + "/" + remote_file)


def error(bot, update):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', bot, update.error)


def get_random_name(y):
    random_str = ''
    for x in range(y):
        if random.choice([True, False]):
            random_str += random.choice(string.ascii_letters).upper()
        else:
            random_str += random.choice(string.ascii_letters)
    return random_str


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.photo, photo_uploader))
    dp.add_handler(MessageHandler(Filters.document, document_uploader))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
