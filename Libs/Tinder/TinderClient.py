import random
import time
from datetime import datetime

import requests
from dateutil.relativedelta import relativedelta

from Libs.Db.StatisticsDb import StatisticsDb
from Libs.Db.TinderDb import TinderDb
from Libs.Tinder.RetryOnError import retry_on_error
from Utils.SecretsProvider import SecretsProvider
from Utils.SettingsProvider import SettingsProvider


class TinderClient:
    def __init__(self):
        self.requests_delay_ms = 2500
        self.headers = {"Host": "api.gotinder.com",
                        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:103.0) Gecko/20100101 Firefox/103.0",
                        "Accept": "application/json",
                        "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate, br",
                        "Content-Type": "application/json",
                        "app-version": "1027301",
                        "tinder-version": "3.38.0",
                        "x-supported-image-formats": "jpeg",
                        "platform": "web",
                        "X-Auth-Token": SecretsProvider.get_tinder_token(),
                        "Origin": "https://tinder.com",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache",
                        "Referer": "https://tinder.com/",
                        "Connection": "keep-alive",
                        "TE": "Trailers"}

        self.my_id = self.get_my_id()

    @retry_on_error
    def get_my_id(self):
        time.sleep(self.requests_delay_ms / 1000)
        response = requests.get(
            "https://api.gotinder.com/v2/profile?locale=ru&include=likes%2Cplus_control%2Cproducts%2Cpurchase%2Cuser",
            headers=self.headers, timeout=1)
        assert response.status_code == 200, f'Cannot get my id, code: {response.status_code}, content: {response.content}'
        data = response.json()
        return data['data']['user']['_id']

    @retry_on_error
    def get_matches(self):
        time.sleep(self.requests_delay_ms / 1000)

        url = "https://api.gotinder.com/v2/matches?locale=ru&count=60&message=0&is_tinder_u=false"
        response = requests.request("GET", url, headers=self.headers, timeout=1)
        assert response.status_code == 200, f'Cannot get matches, code: {response.status_code}, content: {response.content}'
        data = response.json()

        matches = [{'id': m['id'], 'name': m['person']['name']} for m in data['data']['matches']]

        if 'next_page_token' in data['data']:
            next_page_token = data['data']['next_page_token']
        else:
            next_page_token = ''

        while len(next_page_token) != 0:
            time.sleep(self.requests_delay_ms / 1000)

            response = requests.request("GET", url + f'&page_token={next_page_token}', headers=self.headers, timeout=1)
            assert response.status_code == 200, f'Cannot get matches, code: {response.status_code}, content: {response.content}'
            data = response.json()
            matches.extend([{'id': m['id'], 'name': m['person']['name']} for m in data['data']['matches']])

            if 'next_page_token' in data['data']:
                next_page_token = data['data']['next_page_token']
            else:
                next_page_token = ''

        return matches

    @retry_on_error
    def delete_match(self, match_id):
        time.sleep(100 / 1000)

        response = requests.delete(f'https://api.gotinder.com/user/matches/{match_id}?locale=ru', headers=self.headers, timeout=1)

        # assert response.status_code == 200, f"Cannot delete match, code: {response.status_code}, content: {response.content}"

        StatisticsDb.increase_matches_deleted()

    @retry_on_error
    def get_conversations(self, only_new=False):
        conversations = []

        def extend_conversations(conversations_collection, data, only_new=False):
            if only_new:
                only_new_filter = lambda x: not TinderDb.match_exists(x['id'])

                conversations_collection.extend([{'id': m['id'], 'name': m['person']['name']}
                                                 for m in data['data']['matches'] if only_new_filter(m)])
            else:
                conversations_collection.extend([{'id': m['id'], 'name': m['person']['name']}
                                                 for m in data['data']['matches']])

        time.sleep(self.requests_delay_ms / 1000)

        url = "https://api.gotinder.com/v2/matches?locale=ru&count=60&message=1&is_tinder_u=false"
        response = requests.request("GET", url, headers=self.headers, timeout=1)
        assert response.status_code == 200, f'Cannot get conversations, code: {response.status_code}, content: {response.content}'
        data = response.json()

        extend_conversations(conversations_collection=conversations, data=data, only_new=only_new)

        if 'next_page_token' in data['data']:
            next_page_token = data['data']['next_page_token']
        else:
            next_page_token = ''

        while len(next_page_token) != 0:
            time.sleep(self.requests_delay_ms / 1000)

            response = requests.request("GET", url + f'&page_token={next_page_token}', headers=self.headers, timeout=1)
            assert response.status_code == 200, f'Cannot get conversations, code: {response.status_code}, content: {response.content}'
            data = response.json()
            extend_conversations(conversations_collection=conversations, data=data, only_new=only_new)

            if 'next_page_token' in data['data']:
                next_page_token = data['data']['next_page_token']
            else:
                next_page_token = ''

        return conversations

    @retry_on_error
    def send_message(self, match_id, message):
        body = {}
        body['matchId'] = match_id
        body['userId'] = self.my_id

        time.sleep(self.requests_delay_ms / 1000)

        if type(message) == str:
            body['message'] = message
            body[
                'tempMessageId'] = f'0.0{random.randint(100000, 999999)}{random.randint(10000, 99999)}{random.randint(10000, 99999)}'
            requests.post(
                url=f'https://api.gotinder.com/user/matches/{match_id}?locale=ru',
                json=body, headers=self.headers, timeout=1)

        elif type(message) == list:
            for m in message:
                body['message'] = m
                body[
                    'tempMessageId'] = f'0.0{random.randint(100000, 999999)}{random.randint(10000, 99999)}{random.randint(10000, 99999)}'

                requests.post(
                    url=f'https://api.gotinder.com/user/matches/{match_id}?locale=ru',
                    json=body, headers=self.headers, timeout=1)

                time.sleep(SettingsProvider.get_settings()['tinder_send_messages_interval_sec'])

    @retry_on_error
    def get_user_info(self, match_id):
        time.sleep(self.requests_delay_ms / 1000)
        user_id = match_id.replace(self.my_id, '')
        response = requests.get(f'https://api.gotinder.com/user/{user_id}?locale=ru', headers=self.headers, timeout=1)
        assert response.status_code == 200, f'Cannot get user info, code: {response.status_code}, content: {response.content}'
        data = response.json()

        person = data['results']

        job_name = ' '.join([x['title']['name'] for x in person['jobs']]) if person.get('jobs') and person['jobs'][0].get('title') else ''
        job_company = ' '.join([x['company']['name'] for x in person['jobs']]) if person.get('jobs') and person['jobs'][0].get('company') else ''

        school = ''.join([x['name'] for x in person.get('schools', [])])

        distance = person['distance_mi'] * 1.8

        interests = [x['name'] for x in person['user_interests']['selected_interests']] if person.get('user_interests') else []

        bd = '1901-01-01'
        if person.get('birth_date'):
            bd = person['birth_date'].split("T")[0]

        age = relativedelta(datetime.now(), datetime.strptime(bd, "%Y-%M-%d")).years

        city = person['city']['name'] if person.get('city') else ''

        zodiac = ''
        smoke = ''
        pets = ''

        if person.get('selected_descriptors'):

            zodiaс_set = [x for x in person['selected_descriptors'] if x['name'] == 'Знак зодиака']
            if(zodiaс_set):
                zodiac = zodiaс_set[0]['choice_selections'][0]['name']

            smoke_set = [x for x in person['selected_descriptors'] if x['name'] == 'Курение']
            if (smoke_set):
                smoke = smoke_set[0]['choice_selections'][0]['name']

            pets_set = [x for x in person['selected_descriptors'] if x['name'] == 'Питомцы']
            if (pets_set):
                pets = pets_set[0]['choice_selections'][0]['name']

        bio_text = person.get('bio')

        bio = ""

        bio += f"Возраст: {str(age)}" if age < 100 else "Возраст: скрыт"

        if job_name:
            bio += f"\n💼 {job_name} {job_company}"

        if school:
            bio += f"\n👩‍🎓{school}"

        if city:
            bio += f"\n🏠{city}"

        if distance:
            bio += f"\n🧭 {distance} km" if person['distance_mi'] < 10000 else '\n🧭 скрыто'

        if interests:
            bio += f"\nИнтересы: {', '.join(interests)}"

        if zodiac:
            bio += f"\n✨ {zodiac}"

        if smoke:
            bio += f"\n🚬 {smoke}"

        if pets:
            bio += f"\n🙈 {pets}"

        bio += f"\n\n{bio_text}" if bio_text else ''

        info = {'tinder_match_id': match_id,
                'id': person['_id'],
                'name': person['name'],
                'birth_date': bd,
                'age': age,
                'bio': bio,
                'photos': [p['processedFiles'][0]['url'] for p in person['photos']],
                'photos_orig': [p['url'] for p in person['photos']]}

        return info

    @retry_on_error
    def get_messages(self, conversation_id):
        time.sleep(self.requests_delay_ms / 1000)
        url = f'https://api.gotinder.com/v2/matches/{conversation_id}/messages?locale=ru&count=100'
        response = requests.get(url=url, headers=self.headers, timeout=1)
        assert response.status_code == 200, f'Cannot get conversation history, code: {response.status_code}, content: {response.content}'

        data = response.json()
        conversation = []
        for m in data['data']['messages'][::-1]:
            if m in conversation:
                continue
            else:
                conversation.append(m)

        if 'next_page_token' in data['data']:
            next_page_token = data['data']['next_page_token']
        else:
            next_page_token = ''

        while len(next_page_token) != 0:
            time.sleep(self.requests_delay_ms / 1000)
            response = requests.get(url + f'&page_token={next_page_token}', headers=self.headers, timeout=1)
            assert response.status_code == 200, f'Cannot get matches, code: {response.status_code}, content: {response.content}'

            data = response.json()
            conversation = []
            for m in data['data']['messages'][::-1]:
                if m in conversation:
                    continue
                else:
                    conversation.append(m)

            if 'next_page_token' in data['data']:
                next_page_token = data['data']['next_page_token']
            else:
                next_page_token = ''

        girl_responses = [m['message'] for m in conversation if m.get('to') == self.my_id]
        my_requests = [m['message'] for m in conversation if m.get('from') == self.my_id]
        # contact_cards = [m['contact_card'] for m in conversation if m.get('type') == 'contact_card']

        return girl_responses, my_requests, conversation

    @retry_on_error
    def get_girls_for_likes(self):
        time.sleep(self.requests_delay_ms / 1000)

        url = "https://api.gotinder.com/v2/recs/core?locale=ru"
        payload = {}
        response = requests.request("GET", url, headers=self.headers, data=payload, timeout=1)
        assert response.status_code == 200, f'Cannot get girls, code: {response.status_code}, content: {response.content}'

        data = response.json()

        if 'results' not in data['data']:
            return []

        parsed = [{'name': f"{user['user']['name']}",
                   'photos': [p['url'] for p in user['user']['photos']],
                   'id': user['user']['_id'],
                   's_number': user['s_number']}
                  for user in data['data']['results']]

        return parsed

    @retry_on_error
    def set_like(self, id, s_number):
        url = f"https://api.gotinder.com/like/{id}?locale=ru"
        data = {"s_number": s_number}
        response = requests.request("POST", url, headers=self.headers, data=data, timeout=1)

        try:
            data = response.json()
            assert data['status'] == 200, f'Cannot set like to {id}, response status code is {response.status_code}'
        except Exception as e:
            pass
