import random
import time
from datetime import datetime

from Libs.Db.StatisticsDb import StatisticsDb
from Libs.Tinder.TinderClient import TinderClient
from Services.ConversationHandler.ConversationHandler import ConversationHandler
from Services.MessageProvider.MessageProvider import MessageProvider
from Utils.SettingsProvider import SettingsProvider


class TinderHandler:
    def __init__(self):
        self.client = TinderClient()

    def make_swipes(self):

        while True:

            likes_today_set = StatisticsDb.get_statistics_for_today().likes_count
            likes_limit_day = SettingsProvider.get_settings()['likes_per_day_max']
            swipes_delay_multiplier = SettingsProvider.get_settings()['swipes_delay_multiplier']

            girl_age_min = SettingsProvider.get_settings()['girl_age_min']
            girl_age_max = SettingsProvider.get_settings()['girl_age_max']

            current_hour = datetime.now().hour
            permit_likes_hours = [x['hour'] for x in SettingsProvider.get_settings()['permit_like_hours']]

            if likes_today_set < likes_limit_day \
                    and \
                    current_hour in permit_likes_hours:

                delay_for_current_hour = list(filter(lambda x: x['hour'] == current_hour,
                                                     SettingsProvider.get_settings()['permit_like_hours']))[0] \
                    ['like_delay_ms']

                girls = self.client.get_girls_for_likes()
                for girl in girls:

                    if girl_age_min <= int(girl['age']) <= girl_age_max:
                        self.client.set_like(girl['id'], girl['s_number'])
                        StatisticsDb.increase_likes(1)
                        action = 'like'
                    else:
                        self.client.pass_girl(girl['id'], girl['s_number'])
                        action = 'pass'

                    random_swipes_delay_multiplier = random.randint(3, 30) / 10

                    delay = delay_for_current_hour / 1000 * swipes_delay_multiplier * random_swipes_delay_multiplier
                    print(f"{action} {delay}")
                    time.sleep(delay)

            time.sleep(1)

    def begin_conversations(self):
        while True:
            matches = self.client.get_matches()
            time.sleep(SettingsProvider.get_settings()['start_conversations_loop_interval_sec'])
            for match in matches:
                self.client.send_message(match['id'], MessageProvider.messages_for_tinder()[0])

            StatisticsDb.increase_new_matches(len(matches))

    def handle_conversations(self):
        while True:
            time.sleep(SettingsProvider.get_settings()['handle_conversations_loop_interval_sec'])
            conversations_data = self.client.get_conversations(only_new=True)

            for chat in conversations_data:
                ConversationHandler.handle(tinder_client=self.client, match_id=chat['id'])

    def cleanup_matches(self):
        match_ttl_hours = SettingsProvider.get_settings()['match_ttl_hours']

        def _cleanup_matches(conversation, match_ttl_hours):
            ttl = lambda d: (datetime.now() - datetime.strptime(d, '%Y-%m-%dT%H:%M:%S.%f')).seconds > \
                            3600 * match_ttl_hours

            girl_responses, my_requests, whole_conversation = self.client.get_messages(conversation['id'])

            last_message_sent_date = whole_conversation[-1]['sent_date'][:-1]

            if ttl(last_message_sent_date):
                self.client.delete_match(conversation['id'])
                time.sleep(1)

        while True:
            conversations = self.client.get_conversations(only_new=True)
            for conversation in conversations:
                _cleanup_matches(conversation, match_ttl_hours)
