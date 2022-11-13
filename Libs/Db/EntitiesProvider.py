import json
import re

from Utils.TextAnalyzer import TextAnalyzer


class EntitiesProvider:

    @staticmethod
    def get_telegram(telegrams_db):
        try:
            return json.loads(telegrams_db)
        except json.decoder.JSONDecodeError:
            return re.sub(r'''[ "\[\]]''', '', telegrams_db).split(',')

    @staticmethod
    def get_instagram(instagrams_db):
        try:
            return json.loads(instagrams_db)
        except json.decoder.JSONDecodeError:
            found = TextAnalyzer.try_parse_login([instagrams_db])

            found.remove('login')

            return [{'login': x} for x in found]
