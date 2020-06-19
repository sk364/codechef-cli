import json
import os

from requests_html import HTML

from codechefcli.helpers import BASE_URL, COOKIES_FILE_PATH


class MockHTMLResponse:
    def __init__(self, data='<html />', status_code=200, url='', json=""):
        self.html = HTML(html=data)
        self.status_code = status_code
        self.url = f'{BASE_URL}{url}'
        self.text = json

    def json(self, **kwargs):
        return json.loads(self.text)


def fake_login(init_cookies=[]):
    """Fake login by creating cookies file having a fake cookie"""
    cookies = ''
    if init_cookies:
        cookies = "\n".join([
            f"Set-Cookie3: {cookie['name']}={cookie['value']}; path='/'; domain=localhost; \
            port=80000; expires='2120-05-05 23:40:21Z'; version=0" for cookie in init_cookies
        ])
    with open(COOKIES_FILE_PATH, 'w') as f:
        f.write(f'#LWP-Cookies-1.0\nSet-Cookie3: mykey=myvalue; path="/"; domain=localhost; port=80000; \
            expires="2120-05-05 23:40:21Z"; version=0\n{cookies}')


def fake_logout():
    """Fake logout by deleting the cookies"""
    if os.path.exists(COOKIES_FILE_PATH):
        os.remove(COOKIES_FILE_PATH)
