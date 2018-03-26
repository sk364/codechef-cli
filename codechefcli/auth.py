import os

import requests
from bs4 import BeautifulSoup

from .decorators import login_required
from .utils.constants import (BASE_URL, COOKIES_FILE_PATH, EMPTY_AUTH_DATA_MSG,
                              INCORRECT_CREDS_MSG, LOGIN_SUCCESS_MSG,
                              LOGOUT_SUCCESS_MSG, SESSION_LIMIT_MSG)
from .utils.helpers import get_session, request

try:
    from http.cookiejar import LWPCookieJar
except ImportError:
    from cookielib import LWPCookieJar


# Supporting input in Python 2/3
try:
    input = raw_input
except NameError:
    pass


def get_other_active_sessions(session_limit_html):
    """
    :desc: Retrieves disconnect session form action and inputs from webpage.
    :param: `session_limit_html` HTML code containing form.
    :return: (form action url, dictionary form inputs dict)
    """

    soup = BeautifulSoup(session_limit_html, 'html.parser')
    form = soup.find('form', attrs={'id': 'session-limit-page'})
    action = form['action']
    inputs = form.find_all('input')
    inputs = inputs[:-5] + inputs[len(inputs[:-4]):]
    return (action, {inp['name']: inp['value'] for inp in inputs})


def disconnect_sessions(session, disconnect_form_html):
    """
    :desc: Disconnects session when session limit exceeded.
    :param: `session` requests.Session object.
            `disconnect_form_html` form containing list of active sessions.
    :return: `resps` response information dict
    """

    save_cookies = False
    resps = []

    print(SESSION_LIMIT_MSG)
    proceed = input('You need to disconnect other sessions to continue.\n'
                    'Do you want to disconnect other sessions? [Y/n] ')

    if proceed == 'Y' or proceed == '' or proceed == 'y':
        action, other_active_sessions = get_other_active_sessions(disconnect_form_html)
        disconnect_url = BASE_URL + action
        disconnect_req_obj = request(session, 'POST', disconnect_url,
                                     data=other_active_sessions)

        if disconnect_req_obj.status_code == 200:
            resps = [{'data': 'Disconnected other sessions.\nSuccessfully logged in.'}]
            save_cookies = True
        elif disconnect_req_obj.status_code == 503:
            resps = [{'code': 503}]
    else:
        resps = logout(session=session)

    return resps, save_cookies


def login(username, password):
    """
    :desc: Logs a user in. Can disconnect sessions if session limit is exceeded.
    :param: `username` Username of the user
            `password` Password of the user
    :return: `resps` response information dict
    """

    resps = [{
        'data': EMPTY_AUTH_DATA_MSG,
        'code': 400
    }]

    if username and password:
        data = {'name': username, 'pass': password, 'form_id': 'new_login_form'}
        with requests.Session() as session:
            session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)
            req_obj = request(session, 'POST', BASE_URL, data=data)
            save_cookies = False

            if req_obj.status_code == 200:
                if 'Session limit exceeded' in req_obj.text:
                    resps, save_cookies = disconnect_sessions(session, req_obj.text)
                elif 'Logout' in req_obj.text:
                    resps = [{'data': LOGIN_SUCCESS_MSG}]
                    save_cookies = True
                else:
                    resps = [{'data': INCORRECT_CREDS_MSG, 'code': 400}]

                if save_cookies:
                    session.cookies.clear('www.codechef.com', '/', 'login_logout')
                    session.cookies.save(ignore_expires=True, ignore_discard=True)
            elif req_obj.status_code == 503:
                resps = [{'code': 503}]
    return resps


@login_required
def logout(session=None):
    """
    :desc: Logout a user. Delete the cookies.
    :param: `session` Existing session to logout from.
    :return: `resps` response information dict
    """

    session = session or get_session()
    url = BASE_URL + '/logout'
    req_obj = request(session, 'GET', url)

    if req_obj.status_code == 200:
        if os.path.exists(COOKIES_FILE_PATH):
            os.remove(COOKIES_FILE_PATH)
        return [{'data': LOGOUT_SUCCESS_MSG}]
    elif req_obj.status_code == 503:
        return [{'code': 503}]
