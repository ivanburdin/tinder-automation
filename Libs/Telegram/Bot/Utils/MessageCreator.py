import json
import re

from Libs.Db.EntitiesProvider import EntitiesProvider


class MessageCreator:
    @staticmethod
    def make_post_message(match):

        message = f'{match.name}\n\n' \
                  f"{match.interests}" \
                  f"{re.sub(r'[`<>]', ' ', match.bio)}"

        if match.instagram:
            instagrams = EntitiesProvider.get_instagram(match.instagram)

            for instagram in instagrams:
                # is_open = 'open' if instagram['open'] else 'closed'
                message += f'\n\n<a href="instagram.com/{instagram["login"]}">Instagram {instagram["login"]}</a>'

        if match.telegram:

            telegrams = EntitiesProvider.get_telegram(match.telegram)

            for telegram in telegrams:
                message += f'\n\n<a href="t.me/{telegram}">Tg: {telegram}</a>'

        return message
