import telethon

from Libs.Instagram.InstagramChecker import InstagramChecker
from Utils.TextAnalyzer import TextAnalyzer

class ContactsRecognizer:
    @staticmethod
    def get_contacts_from_strings(strings):

        output = {'ig': [], 'tg': [], 'wa': []}

        output['wa'].extend(TextAnalyzer.try_parse_phone(strings))
        output['tg'].extend(TextAnalyzer.try_parse_phone(strings))

        parsed_logins = TextAnalyzer.try_parse_login(strings)
        for login in parsed_logins:

            # ig_result = InstagramChecker.check_ig(login)
            # if ig_result['exists']:
            output['ig'].append({'login': login
                                    # , 'open': ig_result['open']
                                 })

            output['tg'].append(login)

        return output
