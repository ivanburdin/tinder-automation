import json

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from Libs.Db.TinderDb import Match
from Services.MessageProvider.MessageProvider import MessageProvider


class MenuTemplate:

    @staticmethod
    def main_menu_keyboard(match: Match):
        cbd_delete_match = f"delete_match/{match.match_id}/{match.photos_count}"
        cbd_continue_chat = f"continue_chat/{match.match_id}/{match.photos_count}"
        cbd_originals = f"originals/{match.match_id}"
        cbd_delete_post = f"delete_post/{match.match_id}/{match.photos_count}"

        keyboard = [
            [InlineKeyboardButton('Delete Match', callback_data=cbd_delete_match)],
            [InlineKeyboardButton('Continue chat', callback_data=cbd_continue_chat)],
            [InlineKeyboardButton('View Original Photos', callback_data=cbd_originals)],
            [InlineKeyboardButton('Delete this post', callback_data=cbd_delete_post)]]

        if match.telegram:
            telegrams = json.loads(match.telegram)

            if len(telegrams) == 1:
                keyboard.append([InlineKeyboardButton(f'Tg: {telegrams[0]}', callback_data=f'telegram/{match.match_id}/0')])

            elif len(telegrams) == 2:
                keyboard.append([InlineKeyboardButton(f'Tg: {telegrams[0]}', callback_data=f'telegram/{match.match_id}/0')])
                keyboard.append(
                    [
                        InlineKeyboardButton(f'<<', callback_data=f'prev/tg/{match.match_id}'),
                        InlineKeyboardButton(f'>> {telegrams[1]}', callback_data=f'next/tg/{match.match_id}')
                    ]
                )
            elif len(telegrams) > 2:
                keyboard.append([InlineKeyboardButton(f'Tg: {telegrams[1]}', callback_data=f'telegram/{match.match_id}/1')])
                keyboard.append(
                    [
                        InlineKeyboardButton(f'{telegrams[0]} <<', callback_data=f'prev/tg/{match.match_id}'),
                        InlineKeyboardButton(f'>> {telegrams[2]}', callback_data=f'next/tg/{match.match_id}')
                    ]
                )

        if match.instagram:
            instagrams = json.loads(match.instagram)

            # if len(instagrams) == 1:
            #     # open_instagram = 'open' if instagrams[0]["open"] else 'private'
            #     keyboard.append([InlineKeyboardButton(f'iG: {instagrams[0]["login"]}', callback_data=f'instagram/{match.match_id}/0')])
            #
            # elif len(instagrams) == 2:
            #     # open_instagram = 'open' if instagrams[0]["open"] else 'private'
            #     keyboard.append([InlineKeyboardButton(f'iG: {instagrams[0]["login"]}', callback_data=f'instagram/{match.match_id}/0')])
            #     keyboard.append(
            #         [
            #             InlineKeyboardButton(f'<<', callback_data=f'prev/ig/{match.match_id}'),
            #             InlineKeyboardButton(f'>> {instagrams[1]["login"]}', callback_data=f'next/ig/{match.match_id}')
            #         ]
            #     )
            # elif len(instagrams) > 2:
            #     # open_instagram = 'open' if instagrams[1]["open"] else 'private'
            #     keyboard.append([InlineKeyboardButton(f'ig: {instagrams[1]["login"]}', callback_data=f'instagram/{match.match_id}/1')])
            #     keyboard.append(
            #         [
            #             InlineKeyboardButton(f'{instagrams[0]["login"]} <<', callback_data=f'prev/ig/{match.match_id}'),
            #             InlineKeyboardButton(f'>> {instagrams[2]["login"]}', callback_data=f'next/ig/{match.match_id}')
            #         ]
            #     )

        if match.whatsapp:
            whatsapps = json.loads(match.whatsapp)

            if len(whatsapps) == 1:

                keyboard.append([InlineKeyboardButton(text=f'Wa: {whatsapps[0]}',
                                                      callback_data=f'whatsapp/{match.match_id}/0')])

            elif len(whatsapps) == 2:
                keyboard.append([InlineKeyboardButton(text=f'Wa: {whatsapps[0]}',
                                                      callback_data=f'whatsapp/{match.match_id}/0')])

                keyboard.append(
                    [
                        InlineKeyboardButton(f'<<', callback_data=f'prev/wa/{match.match_id}'),
                        InlineKeyboardButton(f'>> {whatsapps[1]}', callback_data=f'next/wa/{match.match_id}')
                    ]
                )
            elif len(whatsapps) > 2:
                keyboard.append([InlineKeyboardButton(text=f'Wa: {whatsapps[1]}',
                                                      callback_data=f'whatsapp/{match.match_id}/1')])
                keyboard.append(
                    [
                        InlineKeyboardButton(f'{whatsapps[0]} <<', callback_data=f'prev/wa/{match.match_id}'),
                        InlineKeyboardButton(f'>> {whatsapps[2]}', callback_data=f'next/wa/{match.match_id}')
                    ]
                )

        return InlineKeyboardMarkup(keyboard)
