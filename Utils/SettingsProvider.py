import json
import os

FOLDER_NAME = 'Settings'

FILE_NAME = 'Settings.json'
FILE_PATH = os.path.abspath(os.path.join(FOLDER_NAME, FILE_NAME))

TINDER_HEADERS_FILE_NAME = 'TinderHeaders.json'
TINDER_HEADERS_FILE_PATH = os.path.abspath(os.path.join(FOLDER_NAME, FILE_NAME))


class SettingsProvider:
    @staticmethod
    def get_settings():
        with open(FILE_PATH) as f:
            settings = json.load(f)
            return settings

    @staticmethod
    def get_tinder_headers():
        with open(TINDER_HEADERS_FILE_PATH) as f:
            headers = json.load(f)
            return headers