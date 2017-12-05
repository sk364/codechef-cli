import os
import subprocess

import requests
from bs4 import BeautifulSoup

from .constants import COOKIES_FILE_PATH

try:
    from http.cookiejar import LWPCookieJar
except ImportError:
    from cookielib import LWPCookieJar


def get_session():
    """
    :desc: Builds session from the saved cookies
    :return: requests.Session object
    """

    session = requests.Session()

    if os.path.exists(COOKIES_FILE_PATH):
        session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)
        session.cookies.load(ignore_discard=True, ignore_expires=True)

    return session


def more(filename='.tmp.codechefcli.tbl'):
    subprocess.call(['cat ' + filename + ' | more'], shell=True)


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
    th_tags = rows[0].find_all('th')
    num_cols = len(th_tags)
    max_len_in_cols = [0] * num_cols
    headings = [[row.text.strip() for row in th_tags]]
    data_rows = headings + [[data.text.strip() for data in row.find_all('td')] for row in rows[1:]]

    for row in data_rows:
        for index, val in enumerate(row):
            if len(val) > max_len_in_cols[index]:
                max_len_in_cols[index] = len(val)

    data_str = ''
    for row in data_rows:
        for index, val in enumerate(row):
            data_str += val + (max_len_in_cols[index] - len(val) + 3) * ' '
        data_str += '\n\n'

    filename = '.tmp.codechefcli.tbl'
    with open(filename, 'w') as f:
        f.write(data_str)

    more(filename=filename)

    if os.path.exists(filename):
        os.remove(filename)


def bold(text):
    """
    :desc: Bold the text by transforming text with ascii codes.
    :param: `text` Text to format.
    :return: `str` Text with ascii codes.
    """

    return '{0}{1}{2}'.format('\033[1m', text, '\033[0m')
