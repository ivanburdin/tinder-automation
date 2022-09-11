import json

from telegram import Update
from telegram.ext import CallbackContext

from Libs.Db.StatisticsDb import StatisticsDb
from Libs.Db.TinderDb import TinderDb
from Libs.Tinder.TinderHandler import TinderHandler
from Services.MessageProvider.MessageProvider import MessageProvider


class MessengersActions:
    def __init__(self, telegram_bot_instance):
        self.telegram_bot_instance = telegram_bot_instance
        self.tinder_handler = TinderHandler()

    def write_telegram(self, update: Update, context: CallbackContext):
        buttons_message_id = update.callback_query.message.message_id
        chat_id = update.callback_query.message.chat_id

        match_id = context.match.group().split('/')[1]
        offset = int(context.match.group().split('/')[2])

        match = TinderDb.get_match(match_id)

        # self.telegram_bot_instance.bot_actions.cleanup_chat(match.photos_count, buttons_message_id, chat_id)

        self.telegram_bot_instance.telegram_client.write_telegram(match, offset)

        new_reply_markup = update.callback_query.message.reply_markup

        def filter_and_update_buttons(button):
            if 'telegram' not in button[0].callback_data:
                return button

            if '✅' not in button[0].text:
                button[0].text = f'✅ {button[0].text} ✅'

            return button

        new_reply_markup.inline_keyboard = [filter_and_update_buttons(b) for b in new_reply_markup.inline_keyboard]

        self.telegram_bot_instance.bot.edit_message_reply_markup(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=new_reply_markup)

        self.tinder_handler.client.send_message(match_id, MessageProvider.message_that_i_wrote_tg())

        StatisticsDb.increase_social_contacts()

    # def write_instagram(self, update: Update, context: CallbackContext):
    #     buttons_message_id = update.callback_query.message.message_id
    #     chat_id = update.callback_query.message.chat_id
    #
    #     match_id = context.match.group().split('/')[1]
    #     offset = int(context.match.group().split('/')[2])
    #
    #     match = TinderDb.get_match(match_id)
    #
    #     self.telegram_bot_instance.bot_actions.cleanup_chat(match.photos_count, buttons_message_id, chat_id)
    #
    #     instagram = json.loads(TinderDb.get_match_igs(match_id=match_id))[offset]['login']
    #
    #     self.telegram_bot_instance.instagram_client.send_message(login=instagram)
    #
    #     instagram_open = json.loads(TinderDb.get_match_igs(match_id=match_id))[offset]['open']
    #     if instagram_open:
    #         self.telegram_bot_instance.instagram_client.set_likes(login=instagram, likes=3)
    #
    #     self.tinder_handler.client.send_message(match_id, MessageProvider.message_that_i_wrote_ig())
    #
    #     StatisticsDb.increase_social_contacts()

    def write_whatsapp(self, update: Update, context: CallbackContext):
        match_id = context.match.group().split('/')[1]
        offset = int(context.match.group().split('/')[2])

        match = TinderDb.get_match(match_id)

        wa_write_button_row_index = -1

        for i, row_of_buttons in enumerate(update.callback_query.message.reply_markup.inline_keyboard):
            if 'whatsapp' in row_of_buttons[0].callback_data:
                wa_write_button_row_index = i
                break

        whatsapps = json.loads(match.whatsapp)

        new_reply_markup = update.callback_query.message.reply_markup
        new_reply_markup.inline_keyboard[wa_write_button_row_index][0].text = f'Wa: {whatsapps[offset]}'
        new_reply_markup.inline_keyboard[wa_write_button_row_index][0].callback_data = None
        new_reply_markup.inline_keyboard[wa_write_button_row_index][0].url = f'https://api.whatsapp.com/send/?phone=' \
                                                                             f'7{whatsapps[offset]}' \
                                                                             f'&text={MessageProvider.messages_for_whatsapp()}'

        if len(new_reply_markup.inline_keyboard) > wa_write_button_row_index + 1:
            if 'prev/wa/' in new_reply_markup.inline_keyboard[wa_write_button_row_index + 1][0].callback_data:
                new_reply_markup.inline_keyboard.pop(wa_write_button_row_index + 1)

        self.telegram_bot_instance.bot.edit_message_reply_markup(
            chat_id=update.callback_query.message.chat_id,
            message_id=update.callback_query.message.message_id,
            reply_markup=new_reply_markup)

        StatisticsDb.increase_social_contacts()

        self.tinder_handler.client.send_message(match_id, MessageProvider.message_that_i_wrote_wa())
