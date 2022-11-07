import time


def telegram_retry(action, **kwargs):
    success = False
    attempts = 0

    while not success:

        if attempts > 25:

            raise Exception(f"telegram_retry failed after {attempts}")

        attempts += 1

        try:

            action(**kwargs)
            success = True

        except Exception as e:

            if not hasattr(e, '__iter__'):
                break

            if "Message to delete not found" in e:
                break

            print(f"[telegram_retry] exception {e}")

            time.sleep(10)
