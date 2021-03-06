import json

from Services.MessageProvider.MessageProvider import MessageProvider


class MessageCreator:
    @staticmethod
    def make_post_message(match):

        message = f'Name: {match.name}, BD: {match.birth_date}, age: {match.age}\n\n' \
                  f'Bio: {match.bio}'

        if match.instagram:
            instagrams = json.loads(match.instagram)
            for instagram in instagrams:
                is_open = 'open' if instagram['open'] else 'closed'
                message += f'\n\n<a href="instagram.com/{instagram["login"]}">Instagram ({is_open}) {instagram["login"]}</a>'

        if match.telegram:
            telegrams = json.loads(match.telegram)
            for telegram in telegrams:
                message += f'\n\n<a href="t.me/{telegram}">Tg: {telegram}</a>'

        return message
