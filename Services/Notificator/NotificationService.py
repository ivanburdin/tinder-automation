import time

from Libs.Db.TinderDb import TinderDb
from Libs.Telegram.Bot.TelegramBot import TelegramBot


class NotificationService:

    @staticmethod
    def notification_service():
        telegram_bot = TelegramBot()

        while True:
            matches_for_notify = TinderDb.get_new_from_notification_queue()

            for match in matches_for_notify:
                telegram_bot.notify_telegram(match)
                TinderDb.push_notification_status(match)
                time.sleep(20)

            time.sleep(10)
