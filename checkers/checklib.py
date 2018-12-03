import random

from requests import Session


class CorruptedService(Exception):
    pass


class MumbleService(Exception):
    pass


class FlagAdderDown(Exception):
    pass


class CheckerSession(Session):
    def __init__(self, timeout=5):
        super().__init__()
        self.request_timeout = timeout
        self.user_agent = self.choose_user_agent()

    @staticmethod
    def choose_user_agent():
        user_agents = [
            None,
            'Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0',
        ]
        return random.choice(user_agents)

    def prepare_request(self, request):
        p = super().prepare_request(request)
        if self.user_agent:
            p.headers.update({'User-Agent': self.user_agent})

        return p

    def request(self, method, url,
                params=None, data=None, headers=None, cookies=None, files=None,
                auth=None, timeout=None, allow_redirects=True, proxies=None,
                hooks=None, stream=None, verify=None, cert=None, json=None):
        if not timeout:
            timeout = self.request_timeout
        # I know about *args,**kwargs. It's for IDE and plugins support.
        return super().request(method, url, params, data, headers, cookies, files, auth, timeout, allow_redirects,
                               proxies, hooks, stream, verify, cert, json)
