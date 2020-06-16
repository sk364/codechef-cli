from requests_html import HTML

from codechefcli.helpers import BASE_URL


class MockHTMLResponse:
    def __init__(self, data='<html />', status_code=200, url=''):
        self.html = HTML(html=data)
        self.status_code = status_code
        self.url = f'{BASE_URL}{url}'
