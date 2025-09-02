import time

import requests

import config


class QueueResponse403(Exception):
    pass

class TooManyRedirects(Exception):
    pass

def get(
        url,
        params=None,
        headers=None,
        max_retries=10,
        retry_delay=60,
        min_interval=1,  # минимальный интервал между запросами (сек)
        stream=False,
        timeout=60
):
    for n in range(max_retries):
        response = None

        # --- лимитер на redis ---
        key = "last_request_ts"
        last_ts = config.REDIS_LOCK.get(key)
        now = time.time()

        if last_ts is not None:
            last_ts = float(last_ts)
            wait = min_interval - (now - last_ts)
            if wait > 0:
                time.sleep(wait)

        config.REDIS_LOCK.set(key, time.time())

        try:
            response = requests.get(
                url=url,
                params=params,
                headers=headers,
                stream=stream,
                timeout=timeout
            )
        except requests.exceptions.ProxyError as e:
            print(f"ProxyError: {str(e)}")
        except requests.exceptions.ConnectionError as e:
            print(f"ConnectionError: {str(e)}")
        except requests.exceptions.TooManyRedirects as e:
            print(f"TooManyRedirects: {str(e)}")
            raise TooManyRedirects(url)
        except Exception as e:
            print(f"UnknownError: {str(e)}")

        if response is not None and response.status_code != 403:
            return response

        time.sleep(retry_delay)

    raise QueueResponse403(url)
