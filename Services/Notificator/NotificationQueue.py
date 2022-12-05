import json

from Libs.Db.StatisticsDb import StatisticsDb
from Libs.Db.TinderDb import TinderDb
from Services.ConversationHandler.ConversationFormatter import ConversationFormatter
from Utils.ContactsRecognizer import ContactsRecognizer
from Utils.SettingsProvider import SettingsProvider


class NotificationQueue:

    @staticmethod
    def try_add(tinder_client,
                match_id,
                girl_responses,
                whole_conversation):

        try:
            user_info = tinder_client.get_user_info(match_id)
        except AssertionError as e:
            return False

        search_strings = []
        search_strings.append(user_info['bio'])
        search_strings.extend(girl_responses)
        contacts = ContactsRecognizer.get_contacts_from_strings(search_strings)

        if len(contacts['ig'] + contacts['tg'] + contacts['wa']) == 0 and not SettingsProvider.get_settings()["ignore_contacts_found_for_continuing_chat"]:
            return False

        pretty_conversation = ConversationFormatter.format(tinder_client.my_id, user_info['name'], whole_conversation)

        dbdata = {'match_id': user_info['tinder_match_id'],
                  'user_id': user_info['id'],
                  'name': user_info['name'],
                  'birth_date': user_info['birth_date'],
                  'bio': user_info['bio'],
                  'age': user_info['age'],
                  'photos': '\n\n'.join(user_info['photos']),
                  'photos_orig': '\n\n'.join(user_info['photos_orig']),
                  'photos_count': len(user_info['photos']),
                  'pretty_conversation': pretty_conversation,
                  'instagram': json.dumps(contacts['ig'], ensure_ascii=False),
                  'telegram': json.dumps(contacts['tg'], ensure_ascii=False),
                  'whatsapp': json.dumps(contacts['wa'], ensure_ascii=False),
                  'notification_status': 'new'}

        TinderDb.upsert_to_notification_queue(**dbdata)

        StatisticsDb.increase_contacts_recieved()
        return True
