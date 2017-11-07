import requests

try:
    from http.cookiejar import LWPCookieJar
except ImportError:
    from cookielib import LWPCookieJar

from bs4 import BeautifulSoup

from .constants import COOKIES_FILE_PATH
from ..decorators import login_required


@login_required
def get_session():
    """
    :desc: Builds session from the saved cookies
    :return: requests.Session object
    """

    session = requests.Session()
    session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)
    session.cookies.load(ignore_discard=True, ignore_expires=True)
    return session


def print_table(table_html):
    """
    :desc: Prints data in tabular format.
    :param: `table_html` HTML text containing <table> tag.
    :return: None
    """

    if not table_html:
        return

    soup = BeautifulSoup(table_html, 'html.parser')
    rows = soup.find('table').find_all('tr')
    headings = '   '.join([row.text for row in rows[0].find_all('th')])
    data_rows = [[data.text for data in row.find_all('td')] for row in rows[1:]]

    spaces = [(len(heading) + 3) * ' ' for heading in headings]

    data_str = ''
    for row in data_rows:
        for index, val in enumerate(row):
            data_str += val + spaces[index]
        data_str += '\n\n'

    print (headings + '\n')
    print (data_str)

