import logging
import time

from requests.exceptions import HTTPError
from requests.packages.urllib3.exceptions import HTTPError as UrlLibHTTPError

from sevenbridges.decorators import retry_on_excs

logger = logging.getLogger(__name__)


@retry_on_excs(excs=(HTTPError, UrlLibHTTPError))
def rate_limit_sleeper(api, response):
    """
    Pauses the execution if rate limit is breached.
    :param api: Api instance.
    :param response: requests.Response object

    """
    while response.status_code == 429:
        headers = response.headers
        remaining_time = headers.get('X-RateLimit-Reset')
        sleep = int(remaining_time) - int(time.time())
        time.sleep(sleep + 5)
        response = api.session.send(response.request)
    return response


@retry_on_excs(excs=(HTTPError, UrlLibHTTPError))
def maintenance_sleeper(api, response):
    """
    Pauses the execution if sevenbridges api is under maintenance.
    :param api: Api instance.
    :param response: requests.Response object.
    """
    while response.status_code == 503:
        response_body = response.json()
        if 'code' in response_body:
            if response_body['code'] == 0:
                time.sleep(300)
                response = api.session.send(response.request)
            else:
                return response
        else:
            return response
    return response


@retry_on_excs(excs=(HTTPError, UrlLibHTTPError))
def general_error_sleeper(api, response):
    """
    Pauses the execution if response status code is > 500.
    :param api: Api instance.
    :param response: requests.Response object

    """
    while response.status_code >= 500:
        time.sleep(300)
        response = api.session.send(response.request)
    return response
