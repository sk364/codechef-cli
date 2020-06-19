import json

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


def fake_login():
    """Fake login by creating cookies file having a fake cookie"""
    with open(COOKIES_FILE_PATH, 'w') as f:
        f.write('#LWP-Cookies-1.0\nSet-Cookie3: mykey=myvalue; path="/"; domain=localhost; port=80000; \
            expires="2120-05-05 23:40:21Z"; version=0')
