import requests
import time

from Services.MessageProvider.MessageProvider import MessageProvider


class InstagramClient:
    def __init__(self, host='', port=''):
        self.host = host or 'localhost'
        self.port = port or '3333'

        alive = False
        max_attempts = 60
        attempts = 0

        while not alive and attempts < max_attempts:
            attempts += 1
            try:
                requests.get(f'http://{self.host}:{self.port}/ready', timeout=20)
                alive = True
                print('instagram client connected to service')
            except:
                time.sleep(1)

        if not alive:
            raise Exception('Instagram in docker not working')

    def send_message(self, login):
        messages = MessageProvider.messages_for_instagram()
        for message in messages:

            response = requests.post(f'http://{self.host}:{self.port}/send/message',
                                     json={'login': login, 'message': message})

            assert response.ok

    def set_likes(self, login, likes=3):
        response = requests.post(f'http://{self.host}:{self.port}/set/likes',
                                 json={'login': login, 'likes': likes})

        assert response.ok