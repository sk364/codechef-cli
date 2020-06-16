from requests_html import HTML


class MockHTMLResponse:
    def __init__(self, data='<html />', status_code=200):
        self.html = HTML(html=data)
        self.status_code = status_code
