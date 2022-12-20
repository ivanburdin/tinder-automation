import json
import os

FILE_NAME = 'Secrets.json'
FOLDER_NAME = 'Settings'
FILE_PATH = os.path.abspath(os.path.join(FOLDER_NAME, FILE_NAME))


class SecretsProvider:
    @staticmethod
    def get_tinder_token():
        with open(FILE_PATH) as f:
            secrets = json.load(f)
            return secrets['tinder_token']

    @staticmethod
    def get_telegram_client_api_id():
        with open(FILE_PATH) as f:
            secrets = json.load(f)
            return secrets['telegram_client']['api_id']

    @staticmethod
    def get_telegram_client_api_hash():
        with open(FILE_PATH) as f:
            secrets = json.load(f)
            return secrets['telegram_client']['api_hash']

    @staticmethod
    def get_telegram_client_phone_number():
        with open(FILE_PATH) as f:
            secrets = json.load(f)
            return secrets['telegram_client']['phone_number']

    @staticmethod
    def get_telegram_bot_token():
        with open(FILE_PATH) as f:
            secrets = json.load(f)
            return secrets['telegram_bot_token']

    @staticmethod
    def get_tinder_headers():
        with open(os.path.abspath(os.path.join(FOLDER_NAME, 'TinderHeaders.txt'))) as f:
            content = f.read()
            lines = [l.strip() for l in content.split('\n')]

            headers = {
                "os-version": "",
                "persistent-device-id": "",
                "user-agent": "",
                "x-hubble-entity-id": "",
                "x-auth-token": "",
                "platform": "",
                "app-session-id": "",
                "app-version": "",
                "user-session-id": "",
            }

            for l in lines:
                header_name, header_value = l.split('\t')

                if header_name in headers:
                    headers[header_name] = header_value


            return headers
