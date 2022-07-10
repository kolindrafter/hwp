import logging
import os
import pandas as pd
import pytz
import re
import numpy as np
import time

from telegram import *
from telegram.ext import *
from requests import *

import yoomoney
from yoomoney import Quickpay
from yoomoney import Client

import datetime
from datetime import datetime
from datetime import timedelta

import threading
from threading import Timer


# Enables logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

PORT = int(os.environ.get('PORT', '8443'))

# We define command handlers. Error handlers also receive the raised TelegramError object in error.
def start(update, context):
    """Sends a message when the command /start is issued."""
    update.message.reply_text('Hi!')

def help(update, context):
    """Sends a message when the command /help is issued."""
    update.message.reply_text('Help!')

def startCommand(update: Update, context: CallbackContext):
    buttons = [[InlineKeyboardButton("Список групп", callback_data='groupList')]]
    context.bot.send_message(chat_id=update.effective_chat.id, text="Привет", reply_markup=ReplyKeyboardMarkup(buttons))

def queryHandler(update: Update, context: CallbackContext):
    query = update.callback_query.data
    update.callback_query.answer()

    context.bot.send_message(chat_id=update.effective_chat.id, text=query)
    context.bot.send_message(chat_id=update.effective_chat.id, text=Update)
    context.bot.send_message(chat_id=update.effective_chat.id, text=CallbackContext)

    print(f"likes => {likes} and dislikes => {dislikes}")


def echo(update, context):
    """Echos the user message."""
    update.message.reply_text(update.message.text)


def error(update, context):
    """Logs Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    """Starts the bot."""
    # Creates the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    TOKEN = '5423176144:AAEAHewAvanY5W4ImVC7P3RoPzlkAdzG0wA'#enter your token here
    APP_NAME='https://helpwithoutprejudice.herokuapp.com/' #Edit the heroku app-name

    updater = Updater(TOKEN, use_context=True)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", startCommand))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CallbackQueryHandler(queryHandler))

    # on noncommand i.e message - echo the message on Telegram
    # dp.add_handler(MessageHandler(Filters.text, echo))

    # log all errors
    dp.add_error_handler(error)
    updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN, webhook_url=APP_NAME + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()