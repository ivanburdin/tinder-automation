import json
import os

FILE_NAME = 'Settings.json'
FOLDER_NAME = 'Settings'
FILE_PATH = os.path.abspath(os.path.join(FOLDER_NAME, FILE_NAME))


class SettingsProvider:
    @staticmethod
    def get_settings():
        with open(FILE_PATH) as f:
            settings = json.load(f)
            return settings
