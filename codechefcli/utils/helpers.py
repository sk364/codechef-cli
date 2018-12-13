import os
import sys
from pydoc import pager
from PIL import Image

import requests
from bs4 import BeautifulSoup
from requests import ReadTimeout
from requests.exceptions import ConnectionError

from .constants import (BCOLORS, COOKIES_FILE_PATH, INTERNET_DOWN_MSG,
                        SERVER_DOWN_MSG, UNAUTHORIZED_MSG, USER_AGENT, IMAGE_DIR)

try:
    from http.cookiejar import LWPCookieJar
except ImportError:
    from cookielib import LWPCookieJar


def get_session(fake_browser=False):
    """
    :desc: Builds session from the saved cookies
    :return: requests.Session object
    """

    session = requests.Session()

    if fake_browser:
        session.headers = {'User-Agent': USER_AGENT}

    if os.path.exists(COOKIES_FILE_PATH):
        session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)
        session.cookies.load(ignore_discard=True, ignore_expires=True)
    return session


def get_username():
    """
    :desc: Retrieves username from session cookies.
    :return: `string` username value or `None` if doesn't exist.
    """

    session = get_session()

    for index, cookie in enumerate(session.cookies):
        if cookie.name == 'username':
            return cookie.value

    return None


def request(session, method, url, **kwargs):
    """
    :desc: Custom wrapper method to add a timeout message
           when there is a `requests.exceptions.ConnectionError`
           or `requests.ReadTimeout` exception.
    :param: `session` requests.Session object
            `method` HTTP method to use
            `url` name of the URL
    :return: requests.Response object.
    """

    try:
        return session.request(method=method, url=url, timeout=(5, 5), **kwargs)
    except (ConnectionError, ReadTimeout):
        print(INTERNET_DOWN_MSG)
        sys.exit(1)


def html_to_list(table_html):
    """
    :desc: Converts the input html table to a 2D list that
           can be given as a input to the print_table function
    :param: `table_html` HTML text contaning <table> tag
    """

    if not table_html:
        return []

    soup = BeautifulSoup(table_html, 'html.parser')
    rows = soup.find('table').find_all('tr')
    th_tags = rows[0].find_all('th')
    headings = [[row.text.strip() for row in th_tags]]
    headings[0] = [x.upper() for x in headings[0]]
    data_rows = headings + [[data.text.strip() for data in row.find_all('td')] for row in rows[1:]]
    return data_rows


def print_table(data_rows):
    """
    :desc: Prints data in tabular format.
    :param: `table_html` HTML text containing <table> tag.
    """

    if len(data_rows) == 0:
        return

    num_cols = len(data_rows[0])
    max_len_in_cols = [0] * num_cols
    for row in data_rows:
        for index, val in enumerate(row):
            if len(val) > max_len_in_cols[index]:
                max_len_in_cols[index] = len(val)

    data_str = ''
    for row in data_rows:
        for index, val in enumerate(row):
            data_str += val + (max_len_in_cols[index] - len(val) + 3) * ' '
        data_str += '\n\n'

    data_str = data_str.strip()
    pager(data_str)
    print(data_str)


def print_inverse_table(table_html):
    """
    :desc: Prints data in "inverse" tabular format.
    :param: `table_html` HTML text containing <table> tag.
    """

    if not table_html:
        return

    soup = BeautifulSoup(table_html, 'html.parser')
    rows = soup.find_all('tr')

    data_str = ''
    for row in rows:
        cols = row.find_all('td')
        for col in cols:
            data_str += ' '.join(col.text.strip().split()) + '    '
        data_str += '\n'

    pager(data_str)
    print(data_str)


def color_text(text, color=None):
    """
    :desc: Colors the text
    """

    if color is None:
        return text

    return '{0}{1}{2}'.format(BCOLORS[color], text, BCOLORS['ENDC'])


def print_response_util(data, extra, data_type, color, is_pager=False, inverse=False):
    """
    :desc: Utility function to print text
    """

    if data is None and extra is None:
        print(color_text('Nothing to show.', 'WARNING'))

    if data is not None:
        if data_type == 'table':
            if inverse:
                print_inverse_table(data)
            else:
                print_table(data)
        elif data_type == 'text':
            if is_pager:
                pager(color_text(data, color))
            print(color_text(data, color))
        elif data_type == 'image_path':
            for file_path in data:
                if file_path != SERVER_DOWN_MSG:
                    img = Image.open(file_path)
                    if img is not None:
                        img.show()

    if extra is not None:
        print(color_text(extra, color))


# TODO: Add robust validations on input `data`
def print_response(data_type='text', code=200, data=None, extra=None, pager=False, inverse=False):
    """
    :desc: Prints response to user.
    :param: `data_type` Type of data
            `data` Data to print
            `extra` Extra messages to print
            `code` Response code
    """

    color = None

    if code == 503:
        data = SERVER_DOWN_MSG
        color = 'FAIL'
    elif code == 404 or code == 400:
        color = 'WARNING'
    elif code == 401:
        color = 'FAIL'
        data = UNAUTHORIZED_MSG

    print_response_util(data, extra, data_type, color, is_pager=pager, inverse=inverse)


def check_download_images(image_url, problem_code, item=1):
    """
    :desc: Downloads the Image if it doesnot exist already
    :param: `image_url` Url of the image to download
            `problem_code` Problem Code of the problem
    """

    url = image_url
    dot_split_url = url.split('.')
    filename = problem_code+'_'+str(item)+'.'+dot_split_url[-1]
    image_dir = os.getcwd() + "/" + IMAGE_DIR
    if(not os.path.isdir(image_dir)):
        #Make the directory
        try:
            os.mkdir(image_dir)
        except OSError:
            print("Error creating directory")
    file_path = image_dir + "/" + filename

    if(not os.path.exists(file_path)):
        session = get_session()

        req_obj = request(session, 'GET', image_url)

        if(req_obj.status_code == 200):

            with open(file_path, 'wb') as handle:
                for block in req_obj.iter_content(1024):
                    if not block:
                        break

                    handle.write(block)


        if req_obj.status_code == 503:
            return SERVER_DOWN_MSG

    return file_path
