import requests

from Utils.TextAnalyzer import TextAnalyzer


class InstagramChecker:
    @staticmethod
    def check_ig(contact_string):
        output = {'exists': False, 'open': False}
        headers = {
                    'accept': '*/*',
                    'accept-encoding': 'gzip, deflate, br',
                    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7,da;q=0.6',
                    'cache-control': 'no-cache',
                    'dnt': 1,
                    'origin': 'https://www.instagram.com',
                    'pragma': 'no-cache',
                    'referer': 'https://www.instagram.com/marinavpm/',
                    'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
                    'sec-ch-ua-mobile': '?0',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'same-origin',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
                    'x-requested-with': 'XMLHttpRequest'
        }

        response = requests.get("https://instagram.com/" + contact_string, headers=headers)
        if response.status_code == 200:
            output['exists'] = True
            try:
                output['open'] = False if '"is_private":true' in response.content.decode('utf-8') else True
            except:
                output['open'] = False

        return output
