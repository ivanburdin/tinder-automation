import time
from datetime import datetime

from Libs.Db.StatisticsDb import StatisticsDb
from Utils.SettingsProvider import SettingsProvider


def log_statistics():
    while True:
        statistics = StatisticsDb.get_statistics_for_today()
        text = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] " \
               f'Likes: {statistics.likes_count} ' \
               f'New Matches: {statistics.new_matches} ' \
               f'Contacts Recieved: {statistics.contacts_recieved} ' \
               f'Matches Deleted: {statistics.matches_deleted} ' \
               f'Social Contacts: {statistics.social_contacts}'
        print(text)

        time.sleep(SettingsProvider.get_settings()['log_interval_sec'])