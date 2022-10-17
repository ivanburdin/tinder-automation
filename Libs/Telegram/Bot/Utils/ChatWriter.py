import re

import telegram
from telegram import InputMediaPhoto

from Libs.Telegram.Bot.Menu.Template import MenuTemplate
from Libs.Telegram.Bot.Utils.MessageCreator import MessageCreator
from Libs.Telegram.Bot.Utils.TimeoutRetrier import telegram_retry
from Utils.ImageDownloader import ImageDownloader


class ChatWriter:
    def __init__(self, telegram_bot_instance):
        self.telegram_bot_instance = telegram_bot_instance

    def send_mediagroup(self, match):
        with self.telegram_bot_instance.chat_lock:
            media_group = list()
            for number, url in enumerate(match.photos.split('\n\n')):
                media_group.append(InputMediaPhoto(media=url, caption=match.pretty_conversation))

            try:
                # telegram_retry(self.telegram_bot_instance.bot.send_media_group,
                #                chat_id=self.telegram_bot_instance.chat_id,
                #                media=media_group[:10]
                #                )

                self.telegram_bot_instance.bot.send_media_group(chat_id=self.telegram_bot_instance.chat_id,
                                                                media=media_group[:10],
                                                                timeout=15)

            except telegram.error.BadRequest as e:
                if 'Media_caption_too_long' in e.message:
                    print(f'Failed to send mediagroup with long caption {len(match.pretty_conversation)} symbols')

                    media_group = list()
                    for number, url in enumerate(match.photos.split('\n\n')):
                        media_group.append(InputMediaPhoto(media=url, caption=match.pretty_conversation[:1023]))
                    self.telegram_bot_instance.bot.send_media_group(chat_id=self.telegram_bot_instance.chat_id,
                                                                    media=media_group[:10])
                else:
                    image_downloader = ImageDownloader()
                    try:
                        media_group = list()
                        for number, url in enumerate(match.photos.split("\n\n")):

                            try:
                                downloaded_file = image_downloader.download_image(url)
                            except Exception as e:
                                if '[ImageDownloader] Cannot download image' in ''.join(e.args):
                                    continue
                                else:
                                    raise e

                            media_group.append(
                                InputMediaPhoto(media=open(downloaded_file, 'rb'), caption=match.pretty_conversation))

                        self.telegram_bot_instance.bot.send_media_group(chat_id=self.telegram_bot_instance.chat_id,
                                                                        media=media_group[:10])


                    finally:
                        image_downloader.cleanup_tmp_dir()


    def send_message(self, match):
        message = MessageCreator.make_post_message(match)
        with self.telegram_bot_instance.chat_lock:

            telegram_retry(self.telegram_bot_instance.bot.send_message,
                           chat_id=self.telegram_bot_instance.chat_id,
                           text=re.sub(r'[`]', ' ', message),
                           parse_mode='HTML',
                           disable_web_page_preview=True,
                           reply_markup=MenuTemplate.main_menu_keyboard(match)
                           )

            # self.telegram_bot_instance.bot.send_message(chat_id=self.telegram_bot_instance.chat_id,
            #                                             text=re.sub(r'[`]', ' ', message),
            #                                             parse_mode='HTML',
            #                                             disable_web_page_preview=True,
            #                                             reply_markup=MenuTemplate.main_menu_keyboard(match),
            #                                             timeout=15
            #                                             )
