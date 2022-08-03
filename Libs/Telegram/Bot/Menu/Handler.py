from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CallbackContext

from Libs.Db.StatisticsDb import StatisticsDb
from Libs.Db.TinderDb import TinderDb
from Libs.Telegram.Bot.Utils.TimeoutRetrier import telegram_retry
from Libs.Tinder.RetryOnError import retry_on_error


class MenuHandler:
    def __init__(self, telegram_bot_instance):
        self.telegram_bot_instance = telegram_bot_instance

    def init(self, update: Update, context: CallbackContext):
        self.telegram_bot_instance.chat_id = update['message']['chat']['id']
        self.telegram_bot_instance.bot.delete_message(chat_id=self.telegram_bot_instance.chat_id,
                                                      message_id=update['message']['message_id'])

    @retry_on_error
    def show_statistics(self, update: Update, context: CallbackContext):
        self.telegram_bot_instance.chat_id = update['message']['chat']['id']
        self.telegram_bot_instance.bot.delete_message(chat_id=self.telegram_bot_instance.chat_id,
                                                      message_id=update['message']['message_id'])

        statistics = StatisticsDb.get_statistics_for_today()

        text = f'Likes: {statistics.likes_count}\n' \
               f'New Matches: {statistics.new_matches}\n' \
               f'Contacts Recieved: {statistics.contacts_recieved}\n' \
               f'Matches Deleted: {statistics.matches_deleted}\n' \
               f'Social Contacts: {statistics.social_contacts}\n'

        telegram_retry(self.telegram_bot_instance.bot.send_message,
                       chat_id=update.message.chat_id,
                       text=text,
                       parse_mode='HTML',
                       disable_web_page_preview=True,
                       reply_markup=InlineKeyboardMarkup(
                           [[InlineKeyboardButton('Delete this message',
                                                  callback_data='delete_message/')]]))

        # self.telegram_bot_instance.bot.send_message(chat_id=update.message.chat_id,
        #                                             text=text,
        #                                             parse_mode='HTML',
        #                                             disable_web_page_preview=True,
        #                                             reply_markup=InlineKeyboardMarkup(
        #                                                 [[InlineKeyboardButton('Delete this message',
        #                                                                        callback_data='delete_message/')]]),
        #                                             timeout=15)

    def clear_db(self, update: Update, context: CallbackContext):
        StatisticsDb.clear_today()
        TinderDb.delete_all_matches()

        telegram_retry(self.telegram_bot_instance.bot.send_message,
                       chat_id=update.message.chat_id,
                       text='Cleared',
                       parse_mode='HTML',
                       disable_web_page_preview=True,
                       reply_markup=InlineKeyboardMarkup(
                           [[InlineKeyboardButton('Delete this message',
                                                  callback_data='delete_message/')]])
                       )

        # self.telegram_bot_instance.bot.send_message(chat_id=update.message.chat_id,
        #                                             text='Cleared',
        #                                             parse_mode='HTML',
        #                                             disable_web_page_preview=True,
        #                                             reply_markup=InlineKeyboardMarkup(
        #                                                 [[InlineKeyboardButton('Delete this message',
        #                                                                        callback_data='delete_message/')]]),
        #                                             timeout=15
        #                                             )
