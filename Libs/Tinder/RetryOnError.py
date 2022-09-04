import time
from xmlrpc.client import ProtocolError

import requests
import traceback


def retry_on_error(method):
    def wrapper(*args, **kwargs):
        attempts = 0
        max_attempts = 100
        retry_delay_s = 10
        protocol_error_retry_delay_s = 120

        while attempts < max_attempts:
            attempts += 1
            try:
                result = method(*args, **kwargs)
                return result
            except requests.exceptions.ReadTimeout:
                time.sleep(retry_delay_s)
            except requests.exceptions.ConnectTimeout:
                time.sleep(retry_delay_s)
            except requests.exceptions.SSLError:
                time.sleep(retry_delay_s)
            except ProtocolError as e:
                print(f"[retry_on_error] Caught ProtocolError exception:\n\n{e.args}\n\n{traceback.format_exc()}")
                time.sleep(protocol_error_retry_delay_s)
            except AssertionError as e:
                print(f"[retry_on_error] Caught assertion exception:\n\n{e.args}\n\n{traceback.format_exc()}")
                time.sleep(retry_delay_s)
            except Exception as e:
                print(f'[retry_on_error] Caught unknown exception:\n\n{e.args}\n\n{traceback.format_exc()}')
                time.sleep(retry_delay_s)

    return wrapper