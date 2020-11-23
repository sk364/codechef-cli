import os
import sys
from http.cookiejar import Cookie, LWPCookieJar
from os.path import expanduser
from pydoc import pager

from requests import ReadTimeout
from requests.exceptions import ConnectionError
from requests_html import HTMLSession

CSRF_TOKEN_INPUT_ID = 'edit-csrfToken'
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


def set_session_cookies(session):
    """Adds any existing cookies to the current session

    Args:
      session: HTMLSession object representing users current session
    """
    session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)


def get_session():
    """Returns a HTMLSession object representing the users current session

    If the user has not logged in, returns a new HTMLSession object
    Otherwise, copies the cookies to the session object and returns it
    """
    session = HTMLSession()

    if os.path.exists(COOKIES_FILE_PATH):
        set_session_cookies(session)
        session.cookies.load(ignore_discard=True, ignore_expires=True)
    return session


def init_session_cookie(name, value, **kwargs):
    """Creates and returns a new Cookie for current session
    """
    return Cookie(version=0, name=name, value=value, port=None, port_specified=False,
                  domain='www.codechef.com', domain_specified=False, domain_initial_dot=False,
                  path='/', path_specified=True, secure=False, expires=None, discard=False,
                  comment=None, comment_url=None, rest={'HttpOnly': None}, rfc2109=False)


def get_username():
    """Returns the username of current user

    Analyzes cookies from current session and gets the username
    """
    session = get_session()

    for index, cookie in enumerate(session.cookies):
        if cookie.name == 'username':
            return cookie.value

    return None


def request(session=None, method="GET", url="", token=None, **kwargs):
    """Makes a HTTP request from current session

    Returns:
      result after making the HTTP request
    """
    if not session:
        session = get_session()
    if token:
        session.headers = getattr(session, 'headers') or {}
        session.headers.update({'X-CSRF-Token': token})

    if BASE_URL not in url:
        url = f'{BASE_URL}{url}'

    try:
        return session.request(method=method, url=url, timeout=(15, 15), **kwargs)
    except (ConnectionError, ReadTimeout):
        print(INTERNET_DOWN_MSG)
        sys.exit(1)


def html_to_list(table):
    """Retrieves table from HTML and converts it to nested list
    """
    if not table:
        return []

    rows = table.find('tr')
    data_rows = [[header.text.strip().upper() for header in rows[0].find('th, td')]]
    for row in rows[1:]:
        data_rows.append([col.text.strip() for col in row.find('td')])
    return data_rows


def get_col_max_lengths(data_rows, num_cols):
    """Calculates the maximum number of characters in every row of data
    Used when printing a table with large text in it
    """
    max_len_in_cols = [0] * num_cols
    for row in data_rows:
        for index, val in enumerate(row):
            if len(val) > max_len_in_cols[index]:
                max_len_in_cols[index] = len(val)
    return max_len_in_cols


def print_table(data_rows, min_num_spaces=MIN_NUM_SPACES, is_pager=True):
    """Prints the table passed to it.

    Used for printing the list of problems from CodeChef

    Args:
      data_rows:
        table containing the data to be printed
      min_num_spaces:
        minimum number of spaces to print between two columns
      is_pager:
        bool value indicating whether to print the table using pager module in pydoc

    Returns:
      String to be printed. The string is obtained from the table, with appropriate
      number of spaces added to make it look more uniform.
    """
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
    if is_pager:
        pager(table_str)
    print(table_str)
    return table_str


def style_text(text, color=None):
    """Styles text in different colors and returns it

    Args:
      text:
        text to be styled
      color:
        color in which text is to be printed

    Returns:
      text styled in the appropriate format, or in case of invalid color the
      original text
    """
    if color is None or BCOLORS.get(color) is None:
        return text

    return '{0}{1}{2}'.format(BCOLORS[color], text, BCOLORS['ENDC'])


def print_response_util(data, extra, data_type, color, is_pager=True):
    """Prints the given data in an appropriate format

    Changes the given string in the given color and returns the new string

    Args:
      data:
        the string to be printed
      extra:
        additional text to be styled
      data_type:
        type of data to be printed, "text", or "table"
      is_pager:
        bool value indicating whether to use the pager method in pydoc package

    Returns:
      The data string formatted in the appropriate color
      The extra string formatted in the appropriate color
    """
    if data is None and extra is None:
        no_data_msg = style_text('Nothing to show.', 'WARNING')
        print(no_data_msg)
        return no_data_msg, None

    return_val = None
    if data is not None:
        if data_type == 'table':
            return_val = print_table(data, is_pager=is_pager)
        elif data_type == 'text':
            if is_pager:
                pager(style_text(data, color))
            return_val = style_text(data, color)
            print(return_val)

    styled_extra = None
    if extra is not None:
        styled_extra = style_text(extra, color)
        print(styled_extra)
    return return_val, styled_extra


def print_response(data_type='text', code=200, data=None, extra=None, **kwargs):
    """Prints the given text in appropriate format.

    Based on whether any data was passed and the HTTP repsonse code given, this
    method prints the data (or an error message) in an appropriate color

    Args:
      data_type:
        type of data to be printed, "text" ot "table"
      code:
        the http response code, used for determining the color of text.
        (ex. errors are printed in red, etc.)
      data:
        the data to be printed
      is_pager:
        optional parameter whether to print data using pager method in pydoc package

    Returns:
      A string formatted in the appropriate format
    """
    color = None

    if code == 503:
        if not data:
            data = SERVER_DOWN_MSG
        color = 'FAIL'
    elif code == 404 or code == 400:
        color = 'WARNING'
    elif code == 401:
        if not data:
            data = UNAUTHORIZED_MSG
        color = 'FAIL'

    is_pager = False
    if not hasattr(kwargs, 'is_pager') and data_type == 'table':
        is_pager = True
    else:
        is_pager = kwargs.get('is_pager', False)

    return print_response_util(data, extra, data_type, color, is_pager=is_pager)


def get_csrf_token(rhtml, selector):
    """
    """
    token = rhtml.find(f"#{selector}", first=True)
    return token and hasattr(token.element, 'value') and token.element.value
