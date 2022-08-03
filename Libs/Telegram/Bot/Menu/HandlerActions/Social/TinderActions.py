from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from Libs.Db.StatisticsDb import StatisticsDb
from Libs.Db.TinderDb import TinderDb
from Libs.Telegram.Bot.Menu.Template import MenuTemplate
from Libs.Telegram.Bot.Utils.MessageCreator import MessageCreator
from Libs.Telegram.Bot.Utils.TimeoutRetrier import telegram_retry
from Libs.Tinder.TinderHandler import TinderHandler
from Services.ConversationHandler.ConversationHandler import ConversationHandler


class TinderActions:
    def __init__(self, telegram_bot_instance):
        self.telegram_bot_instance = telegram_bot_instance
        self.tinder_handler = TinderHandler()

    def delete_match(self, update: Update, context: CallbackContext):
        callback_data = context.match.group().split('/')
        match_id = callback_data[1]
        photos_count = callback_data[2]

        chat_id = update.callback_query.message.chat_id
        buttons_message_id = update.callback_query.message.message_id

        self.telegram_bot_instance.bot_actions.cleanup_chat(photos_count, buttons_message_id, chat_id)

        TinderDb.delete_match(match_id)
        self.tinder_handler.client.delete_match(match_id)

    def continue_chat(self, update: Update, context: CallbackContext):
        _, match_id, photos_count = context.match.group().split('/')

        chat_id = update.callback_query.message.chat_id
        buttons_message_id = update.callback_query.message.message_id

        self.telegram_bot_instance.bot_actions.cleanup_chat(photos_count, buttons_message_id, chat_id)

        ConversationHandler.continue_chat(tinder_client=self.tinder_handler.client, match_id=match_id)

        StatisticsDb.derease_contacts_recieved()

        TinderDb.delete_match(match_id)

    def view_original_photos(self, update: Update, context: CallbackContext):
        match_id = context.match.group().split('/')[1]
        match = TinderDb.get_match(match_id)
        ph_orig = match.photos_orig

        chat_id = update.callback_query.message.chat_id

        telegram_retry(self.telegram_bot_instance.bot.send_message,
                       chat_id=chat_id,
                       text=ph_orig,
                       reply_markup=InlineKeyboardMarkup(
                           [[InlineKeyboardButton('Delete this message',
                                                  callback_data='delete_message/')]])
                       )


        # self.telegram_bot_instance.bot.send_message(chat_id=chat_id,
        #                                             text=ph_orig,
        #                                             reply_markup=InlineKeyboardMarkup(
        #                                                 [[InlineKeyboardButton('Delete this message',
        #                                                                        callback_data='delete_message/')]]),
        #                                             timeout=15)

    def get_info(self, update: Update, context: CallbackContext):
        query = update.message.text
        query.replace("@", "")
        match = TinderDb.search_match(query.replace("@", ""))

        if query == '/start':

            telegram_retry(self.telegram_bot_instance.bot.send_message,
                           chat_id=update.message.chat_id,
                           text='started',
                           parse_mode='HTML',
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup(
                               [[InlineKeyboardButton('Delete this message',
                                                      callback_data='delete_message/')]])
                           )

            # self.telegram_bot_instance.bot.send_message(chat_id=update.message.chat_id,
            #                                             text='started',
            #                                             parse_mode='HTML',
            #                                             disable_web_page_preview=True,
            #                                             reply_markup=InlineKeyboardMarkup(
            #                                                 [[InlineKeyboardButton('Delete this message',
            #                                                                        callback_data='delete_message/')]]),
            #                                             timeout=15)

            self.telegram_bot_instance.bot.delete_message(chat_id=update.message.chat_id,
                                                          message_id=update.message.message_id)

            return

        if match is not None:
            self.telegram_bot_instance.chat_writer.send_mediagroup(match)
            self.telegram_bot_instance.chat_writer.send_message(match)


        else:

            telegram_retry(self.telegram_bot_instance.bot.send_message,
                           chat_id=update.message.chat_id,
                           text=f"<b>Not found for query: {query}</b>",
                           parse_mode='HTML',
                           disable_web_page_preview=True,
                           reply_markup=InlineKeyboardMarkup(
                               [[InlineKeyboardButton('Delete this message',
                                                      callback_data='delete_message/')]])
                           )

            # self.telegram_bot_instance.bot.send_message(chat_id=update.message.chat_id,
            #                                             text=f"<b>Not found for query: {query}</b>",
            #                                             parse_mode='HTML',
            #                                             disable_web_page_preview=True,
            #                                             reply_markup=InlineKeyboardMarkup(
            #                                                 [[InlineKeyboardButton('Delete this message',
            #                                                                        callback_data='delete_message/')]]),
            #                                             timeout=15)

        # remove search query
        self.telegram_bot_instance.bot.delete_message(chat_id=update.message.chat_id,
                                                      message_id=update.message.message_id)
