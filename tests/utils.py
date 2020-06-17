import json

from requests_html import HTML

from codechefcli.helpers import BASE_URL


class MockHTMLResponse:
    def __init__(self, data='<html />', status_code=200, url='', json=""):
        self.html = HTML(html=data)
        self.status_code = status_code
        self.url = f'{BASE_URL}{url}'
        self.text = json

    def json(self, **kwargs):
        return json.loads(self.text)
