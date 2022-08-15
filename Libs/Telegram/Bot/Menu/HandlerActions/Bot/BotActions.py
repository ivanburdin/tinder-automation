import json
import time

from telegram import InlineKeyboardButton, Update
from telegram.ext import CallbackContext

from Libs.Db.TinderDb import TinderDb
from Libs.Telegram.Bot.Utils.TimeoutRetrier import telegram_retry


class BotActions:
    def __init__(self, telegram_bot_instance):
        self.telegram_bot_instance = telegram_bot_instance

    def delete_message(self, update: Update, context: CallbackContext):
        self.telegram_bot_instance.bot.delete_message(chat_id=update.callback_query.message.chat_id,
                                                      message_id=update.callback_query.message.message_id)

    def delete_post(self, update: Update, context: CallbackContext):
        photos_count = int(context.match.group().split('/')[2])

        chat_id = update.callback_query.message.chat_id
        buttons_message_id = update.callback_query.message.message_id

        self.cleanup_chat(photos_count, buttons_message_id, chat_id)

    def cleanup_chat(self, photos_sent, buttons_message_id, chat_id):
        with self.telegram_bot_instance.chat_lock:
            photos_sent = int(photos_sent)
            delete_messages_ids = list(range(buttons_message_id - photos_sent, buttons_message_id + 1))
            for id in delete_messages_ids:
                try:
                    # telegram_retry(self.telegram_bot_instance.bot.delete_message, chat_id=chat_id, message_id=id)
                    self.telegram_bot_instance.bot.delete_message(chat_id=chat_id, message_id=id)
                    print(f'deleted tg message {id}')
                except Exception as e:
                    time.sleep(0.5)
                    print(f'exception {e} while deleting tg message {id}')

    def switch_instagram(self, update: Update, context: CallbackContext):
        callback_data = update.callback_query.data
        direction, _, tinder_match_id = callback_data.split('/')

        ig_write_button_row_index = -1
        ig_switch_buttons_row_index = -1

        for i, row_of_buttons in enumerate(update.callback_query.message.reply_markup.inline_keyboard):
            if 'instagram' in row_of_buttons[0].callback_data:
                ig_write_button_row_index = i
                ig_switch_buttons_row_index = i + 1
                position = int(update.callback_query.message.reply_markup.inline_keyboard[i] \
                                   [0].callback_data.split('/')[2])
                break

        instagrams = json.loads(TinderDb.get_match_igs(match_id=tinder_match_id))

        if direction == 'next':
            position += 1

            if position > len(instagrams) - 1:
                return

        elif direction == 'prev':
            position -= 1

            if position < 0:
                return

        new_instagram_login = instagrams[position]['login']

        new_reply_markup = update.callback_query.message.reply_markup
        open_instagram = 'open' if instagrams[position]["open"] else 'private'
        new_reply_markup.inline_keyboard[ig_write_button_row_index][0].text = f'iG: {new_instagram_login} ' \
                                                                              f'({open_instagram})'
        new_reply_markup.inline_keyboard[ig_write_button_row_index][
            0].callback_data = f'instagram/{tinder_match_id}/{position}'

        if position == 0:

            new_reply_markup.inline_keyboard[ig_switch_buttons_row_index] = [
                InlineKeyboardButton(f'<<', callback_data=f'prev/ig/{tinder_match_id}'),
                InlineKeyboardButton(f'>> {instagrams[position + 1]["login"]}', callback_data=f'next/ig/{tinder_match_id}')
            ]

        elif position == len(instagrams) - 1:

            new_reply_markup.inline_keyboard[ig_switch_buttons_row_index] = [
                InlineKeyboardButton(f'<< {instagrams[position - 1]["login"]}', callback_data=f'prev/ig/{tinder_match_id}'),
                InlineKeyboardButton(f'>>', callback_data=f'next/ig/{tinder_match_id}')
            ]

        else:

            new_reply_markup.inline_keyboard[ig_switch_buttons_row_index] = [
                InlineKeyboardButton(f'<< {instagrams[position - 1]["login"]}', callback_data=f'prev/ig/{tinder_match_id}'),
                InlineKeyboardButton(f'>> {instagrams[position + 1]["login"]}', callback_data=f'next/ig/{tinder_match_id}')
            ]

        self.telegram_bot_instance.bot.edit_message_reply_markup(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=new_reply_markup)

    def switch_telegram(self, update: Update, context: CallbackContext):
        callback_data = update.callback_query.data
        direction, _, tinder_match_id = callback_data.split('/')

        tg_write_button_row_index = -1
        tg_switch_buttons_row_index = -1

        for i, row_of_buttons in enumerate(update.callback_query.message.reply_markup.inline_keyboard):
            if 'telegram' in row_of_buttons[0].callback_data:
                tg_write_button_row_index = i
                tg_switch_buttons_row_index = i + 1
                position = int(update.callback_query.message.reply_markup.inline_keyboard[i] \
                    [0].callback_data.split('/')[2])
                break

        telegrams = json.loads(TinderDb.get_match_tgs(match_id=tinder_match_id))

        if direction == 'next':
            position += 1

            if position > len(telegrams) - 1:
                return

        elif direction == 'prev':
            position -= 1

            if position < 0:
                return

        new_telegram_login = telegrams[position]

        new_reply_markup = update.callback_query.message.reply_markup
        new_reply_markup.inline_keyboard[tg_write_button_row_index][0].text = f'Tg: {new_telegram_login}'
        new_reply_markup.inline_keyboard[tg_write_button_row_index][0].callback_data = f'telegram/{tinder_match_id}/{position}'

        if position == 0:

            new_reply_markup.inline_keyboard[tg_switch_buttons_row_index] = [
                        InlineKeyboardButton(f'<<', callback_data=f'prev/tg/{tinder_match_id}'),
                        InlineKeyboardButton(f'>> {telegrams[position + 1]}', callback_data=f'next/tg/{tinder_match_id}')
                    ]

        elif position == len(telegrams) - 1:

            new_reply_markup.inline_keyboard[tg_switch_buttons_row_index] = [
                        InlineKeyboardButton(f'<< {telegrams[position - 1]}', callback_data=f'prev/tg/{tinder_match_id}'),
                        InlineKeyboardButton(f'>>', callback_data=f'next/tg/{tinder_match_id}')
                    ]

        else:

            new_reply_markup.inline_keyboard[tg_switch_buttons_row_index] = [
                InlineKeyboardButton(f'<< {telegrams[position - 1]}', callback_data=f'prev/tg/{tinder_match_id}'),
                InlineKeyboardButton(f'>> {telegrams[position + 1]}', callback_data=f'next/tg/{tinder_match_id}')
            ]


        self.telegram_bot_instance.bot.edit_message_reply_markup(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=new_reply_markup)

    def switch_whatsapp(self, update: Update, context: CallbackContext):
        callback_data = update.callback_query.data
        direction, _, tinder_match_id = callback_data.split('/')

        wa_write_button_row_index = -1
        wa_switch_buttons_row_index = -1

        for i, row_of_buttons in enumerate(update.callback_query.message.reply_markup.inline_keyboard):
            if 'whatsapp' in row_of_buttons[0].callback_data:
                wa_write_button_row_index = i
                wa_switch_buttons_row_index = i + 1
                position = int(update.callback_query.message.reply_markup.inline_keyboard[i] \
                    [0].callback_data.split('/')[2])
                break

        whatsapps = json.loads(TinderDb.get_match_was(match_id=tinder_match_id))

        if direction == 'next':
            position += 1

            if position > len(whatsapps) - 1:
                return

        elif direction == 'prev':
            position -= 1

            if position < 0:
                return

        new_whatsapp_login = whatsapps[position]

        new_reply_markup = update.callback_query.message.reply_markup
        new_reply_markup.inline_keyboard[wa_write_button_row_index][0].text = f'Wa: {new_whatsapp_login}'
        new_reply_markup.inline_keyboard[wa_write_button_row_index][0].callback_data = f'whatsapp/{tinder_match_id}/{position}'

        if position == 0:

            new_reply_markup.inline_keyboard[wa_switch_buttons_row_index] = [
                        InlineKeyboardButton(f'<<', callback_data=f'prev/wa/{tinder_match_id}'),
                        InlineKeyboardButton(f'>> {whatsapps[position + 1]}', callback_data=f'next/wa/{tinder_match_id}')
                    ]

        elif position == len(whatsapps) - 1:

            new_reply_markup.inline_keyboard[wa_switch_buttons_row_index] = [
                        InlineKeyboardButton(f'<< {whatsapps[position - 1]}', callback_data=f'prev/wa/{tinder_match_id}'),
                        InlineKeyboardButton(f'>>', callback_data=f'next/wa/{tinder_match_id}')
                    ]

        else:

            new_reply_markup.inline_keyboard[wa_switch_buttons_row_index] = [
                InlineKeyboardButton(f'<< {whatsapps[position - 1]}', callback_data=f'prev/wa/{tinder_match_id}'),
                InlineKeyboardButton(f'>> {whatsapps[position + 1]}', callback_data=f'next/wa/{tinder_match_id}')
            ]


        self.telegram_bot_instance.bot.edit_message_reply_markup(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=new_reply_markup)