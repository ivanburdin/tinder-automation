import re


class TextAnalyzer:

    @staticmethod
    def try_parse_login(strings):
        all_data = ''.join(strings)

        cleared = re.sub(r'instagram|telegram|whatsapp|inst|tik|tok|http|https|[() ,;:-@]|/|\||\\',
                         ' ',
                         all_data,
                         flags=re.IGNORECASE)

        found_contacts = []
        for result in re.findall(r'[a-z0-9_.-]{5,}', cleared, flags=re.IGNORECASE):
            if not TextAnalyzer.try_parse_phone(result):
                found_contacts.append(result)

        return list(set(found_contacts))

    @staticmethod
    def try_parse_phone(strings):

        parsed_groups = re.findall(r'(\d{10,})'
                                   r'|(\d{3,}\D{1}\d{3,}\D{1}\d{2,}\D{1}\d{2,})', ''.join(strings))
        parsed_phone_nums = []
        for group in parsed_groups:
            for result in [result for result in group if len(result)]:
                parsed_phone_nums.append(re.sub(r'\D', '', result)[-10:])

        return list(set(parsed_phone_nums))
