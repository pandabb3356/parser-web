import requests

from functools import wraps


class BaseApiHelper(object):
    @classmethod
    def handle_req(cls, func):
        @wraps(func)
        def wrapper(api_service, url, *args, **kwargs):
            new_url = api_service.generate_url(url)
            kwargs['headers'] = dict(api_service.headers)

            return func(api_service, new_url, *args, **kwargs)
        return wrapper


class BaseApiService(object):
    helper = BaseApiHelper

    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept': 'application/json'
    }

    def __init__(self, server_url):
        self.server_url = server_url

    def generate_url(self, relative_url):
        return "{}{}".format(self.server_url, relative_url)

    @helper.handle_req
    def get(self, url, *args, **kwargs):
        return requests.get(url, *args, **kwargs)

    @helper.handle_req
    def post(self, url, *args, **kwargs):
        return requests.post(url, *args, **kwargs)

    @helper.handle_req
    def put(self, url, *args, **kwargs):
        return requests.put(url, *args, **kwargs)
