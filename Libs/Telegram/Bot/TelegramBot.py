import time
from threading import Lock

from telegram import Bot
from telegram.ext import CommandHandler, CallbackQueryHandler
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

# from Libs.Instagram.InstagramClient import InstagramClient
from Libs.Telegram.Bot.Menu.Handler import MenuHandler
from Libs.Telegram.Bot.Menu.HandlerActions.Bot.BotActions import BotActions
from Libs.Telegram.Bot.Menu.HandlerActions.Social.MessengersActions import MessengersActions
from Libs.Telegram.Bot.Menu.HandlerActions.Social.TinderActions import TinderActions
from Libs.Telegram.Bot.Utils.ChatWriter import ChatWriter
from Libs.Telegram.Bot.Utils.TimeoutRetrier import telegram_retry
from Libs.Telegram.Client.TelegramUserClient import TelegramUserClient
from Utils.SecretsProvider import SecretsProvider


class TelegramBot:
    def __init__(self):
        self.chat_lock = Lock()
        self.token = SecretsProvider.get_telegram_bot_token()

        self.bot = Bot(self.token)
        self.bot.get_updates()

        # self.instagram_client = InstagramClient()
        self.telegram_client = TelegramUserClient()

        self.chat_writer = ChatWriter(telegram_bot_instance=self)

        self.menu_handler = MenuHandler(telegram_bot_instance=self)
        self.delay_ms = 200
        self.chat_id = 0

        self.updater = Updater(self.token, use_context=True)

        self.bot_actions = BotActions(telegram_bot_instance=self)
        self.tinder_actions = TinderActions(telegram_bot_instance=self)
        self.messengersActions = MessengersActions(telegram_bot_instance=self)

        self._register_handlers()
        self.updater.start_polling()
        self.await_for_chat_id()

    def notify_telegram(self, match):

        # self.chat_writer.send_mediagroup(match)
        telegram_retry(self.chat_writer.send_mediagroup, match=match)
        time.sleep(2)
        self.chat_writer.send_message(match)

    def _register_handlers(self):
        # Common
        self.updater.dispatcher.add_handler(CommandHandler('init', self.menu_handler.init))
        self.updater.dispatcher.add_handler(CommandHandler('stat', self.menu_handler.show_statistics, pass_user_data=True))
        self.updater.dispatcher.add_handler(CommandHandler('clear_db', self.menu_handler.clear_db, pass_user_data=True))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.delete_message, pattern=r'delete_message/'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.delete_post, pattern=r'delete_post/[\w/]+'))

        # Switch
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.switch_telegram, pattern=r'prev/tg'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.switch_telegram, pattern=r'next/tg'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.switch_instagram, pattern=r'prev/ig'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.switch_instagram, pattern=r'next/ig'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.switch_whatsapp, pattern=r'prev/wa'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.bot_actions.switch_whatsapp, pattern=r'next/wa'))

        # Tinder
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tinder_actions.delete_match, pattern=r'delete_m/[\w/]+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tinder_actions.update_post, pattern=r'update_p/[\w/]+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tinder_actions.send_contacts_in_chat, pattern=r'snd_tg_cht/[\w/]+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tinder_actions.continue_chat, pattern=r'continue_cht/[\w/]+'))
        self.updater.dispatcher.add_handler(CallbackQueryHandler(self.tinder_actions.view_original_photos, pattern=r'originals/[\w]+'))
        self.updater.dispatcher.add_handler(MessageHandler(filters=Filters.text, callback=self.tinder_actions.get_info))

        # Social
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(self.messengersActions.write_telegram, pattern=r'telegram/[\w]+/[\d]+'))
        # self.updater.dispatcher.add_handler(
        #     CallbackQueryHandler(self.messengersActions.write_instagram, pattern=r'instagram/[\w]+/[\d]+'))
        self.updater.dispatcher.add_handler(
            CallbackQueryHandler(self.messengersActions.write_whatsapp, pattern=r'whatsapp/[\w]+/[\d]+'))

    def await_for_chat_id(self):
        for x in range(20):
            time.sleep(1)
            if self.chat_id:
                print('telegram bot connected to chat', self.chat_id)
                break
