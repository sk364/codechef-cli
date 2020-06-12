import os
import sys
from http.cookiejar import Cookie, LWPCookieJar
from os.path import expanduser
from pydoc import pager

from requests import ReadTimeout
from requests.exceptions import ConnectionError
from requests_html import HTMLSession

MIN_NUM_SPACES = 3
BASE_URL = 'https://www.codechef.com'
SERVER_DOWN_MSG = 'Please try again later. Seems like CodeChef server is down!'
INTERNET_DOWN_MSG = 'Nothing to show. Check your internet connection.'
UNAUTHORIZED_MSG = 'You are not logged in.'
COOKIES_FILE_PATH = expanduser('~') + '/.cookies'
BCOLORS = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}


def get_session():
    session = HTMLSession()

    if os.path.exists(COOKIES_FILE_PATH):
        session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)
        session.cookies.load(ignore_discard=True, ignore_expires=True)
    return session


def set_session_cookies(session):
    session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)


def init_session_cookie(name, value, **kwargs):
    return Cookie(version=0, name=name, value=value, port=None, port_specified=False,
                  domain='www.codechef.com', domain_specified=False, domain_initial_dot=False,
                  path='/', path_specified=True, secure=False, expires=None, discard=False,
                  comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)


def get_username():
    session = get_session()

    for index, cookie in enumerate(session.cookies):
        if cookie.name == 'username':
            return cookie.value

    return None


def request(session=None, method="GET", url="", token=None, **kwargs):
    if not session:
        session = get_session()
    if token:
        session.headers = getattr(session, 'headers') or {}
        session.headers.update({'X-CSRF-Token': token})

    try:
        return session.request(method=method, url=f'{BASE_URL}{url}', timeout=(15, 15), **kwargs)
    except (ConnectionError, ReadTimeout):
        print(INTERNET_DOWN_MSG)
        sys.exit(1)


def html_to_list(table):
    if not table:
        return []

    rows = table.find('tr')
    data_rows = [[header.text.strip().upper() for header in rows[0].find('th')]]
    for row in rows[1:]:
        data_rows.append([col.text.strip() for col in row.find('td')])
    return data_rows


def get_col_max_lengths(data_rows, num_cols):
    max_len_in_cols = [0] * num_cols
    for row in data_rows:
        for index, val in enumerate(row):
            if len(val) > max_len_in_cols[index]:
                max_len_in_cols[index] = len(val)
    return max_len_in_cols


def print_table(data_rows, min_num_spaces=MIN_NUM_SPACES):
    if len(data_rows) == 0:
        return

    max_len_in_cols = get_col_max_lengths(data_rows, len(data_rows[0]))

    table = []
    for row in data_rows:
        _row = []
        for index, val in enumerate(row):
            num_spaces = max_len_in_cols[index] - len(val) + min_num_spaces
            _row.append(val + (num_spaces * ' '))
        table.append("".join(_row))

    table_str = '\n\n'.join(table)
    pager(table_str)
    print(table_str)


def style_text(text, color=None):
    if color is None:
        return text

    return '{0}{1}{2}'.format(BCOLORS[color], text, BCOLORS['ENDC'])


def print_response_util(data, extra, data_type, color, is_pager=False):
    if data is None and extra is None:
        print(style_text('Nothing to show.', 'WARNING'))

    if data is not None:
        if data_type == 'table':
            print_table(data)
        elif data_type == 'text':
            if is_pager:
                pager(style_text(data, color))
            print(style_text(data, color))

    if extra is not None:
        print(style_text(extra, color))


def print_response(data_type='text', code=200, data=None, extra=None, pager=False):
    color = None

    if code == 503:
        if not data:
            data = SERVER_DOWN_MSG
        color = 'FAIL'
    elif code == 404 or code == 400:
        color = 'WARNING'
    elif code == 401:
        color = 'FAIL'
        if not data:
            data = UNAUTHORIZED_MSG

    print_response_util(data, extra, data_type, color, is_pager=pager)


def get_csrf_token(rhtml, selector):
    token = rhtml.find(f"#{selector}", first=True)
    return token and hasattr(token.element, 'value') and token.element.value
