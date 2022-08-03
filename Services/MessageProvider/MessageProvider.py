import json
import os

FILE_NAME = 'Messages.json'
FOLDER_NAME = 'Settings'
FILE_PATH = os.path.abspath(os.path.join(FOLDER_NAME, FILE_NAME))


class MessageProvider:
    @staticmethod
    def messages_for_tinder():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['tinder']['messages']

    @staticmethod
    def notification_threshold():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['tinder']['notification_threshold']

    @staticmethod
    def messages_for_instagram():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['instagram']

    @staticmethod
    def messages_for_telegram():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['telegram']

    @staticmethod
    def messages_for_whatsapp():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['whatsapp']

    @staticmethod
    def message_that_i_wrote_tg():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['i_wrote_tg']

    @staticmethod
    def message_that_i_wrote_ig():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['i_wrote_ig']

    @staticmethod
    def message_that_i_wrote_wa():
        with open(FILE_PATH) as f:
            messages = json.load(f)
            return messages['i_wrote_wa']