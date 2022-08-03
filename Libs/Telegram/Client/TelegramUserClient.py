import asyncio
import json
import os
import sqlite3
import time
from threading import Lock

from telethon.sync import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl.types import InputPhoneContact

from Libs.Db.TinderDb import Match, TinderDb
from Services.MessageProvider.MessageProvider import MessageProvider
from Utils.SecretsProvider import SecretsProvider
from Utils.TextAnalyzer import TextAnalyzer

CLIENT_LOCK = Lock()
CLIENT_CREATED = False
PATH_TO_DB = os.path.join(os.path.abspath('storage'), 'tg_user_client_session_db.session')


class TelegramUserClient:

    def __new__(cls):
        with CLIENT_LOCK:
            if not hasattr(cls, 'instance'):
                cls.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(cls.loop)

                cls.api_id = SecretsProvider.get_telegram_client_api_id()
                cls.api_hash = SecretsProvider.get_telegram_client_api_hash()
                cls.phone = SecretsProvider.get_telegram_client_phone_number()

                cls.client = TelegramClient('storage/tg_user_client_session_db', cls.api_id, cls.api_hash,
                                            loop=cls.loop, device_model="iPhone 13 Pro Max", app_version='3.7.3', system_version='Windows 10')

                try:
                    cls.client.connect()
                except sqlite3.OperationalError:
                    os.remove(PATH_TO_DB)
                    cls.client.connect()

                if not cls.client.is_user_authorized():
                    cls.client.send_code_request(cls.phone)
                    cls.client.sign_in(cls.phone, input('Enter the code: '))

                cls.client.send_message("@tindernewsbot", '/init')  # connect to bot

                cls.instance = super(TelegramUserClient, cls).__new__(cls)

            return cls.instance

    def write_telegram(self, match: Match, offset: int):
        telegram = json.loads(TinderDb.get_match_tgs(match_id=match.match_id))[offset]
        asyncio.set_event_loop(self.loop)

        messages = MessageProvider.messages_for_telegram()

        if TextAnalyzer.try_parse_login(strings=[telegram]):
            receiver = f"@{telegram}"

            for message in messages:
                try:
                    self.client.send_message(receiver, message)

                    if message != messages[-1]:
                        time.sleep(5)

                except ValueError as e:
                    print(e.args)

        elif TextAnalyzer.try_parse_phone(telegram):
            contact = InputPhoneContact(
                client_id=0,  # For new contacts use client_id = 0
                phone=f"+7{telegram}",
                first_name=f"{match.name} {match.age}",
                last_name='Tinder')

            c = self.client(ImportContactsRequest([contact]))
            if c.users:
                for message in messages:
                    self.client.send_message(c.users[0], message)

                    if message != messages[-1]:
                        time.sleep(5)
