import os
from getpass import getpass

from requests_html import HTMLSession

from codechefcli.decorators import login_required
from codechefcli.helpers import (COOKIES_FILE_PATH, get_csrf_token,
                                 init_session_cookie, request,
                                 set_session_cookies)

CSRF_TOKEN_INPUT_ID = 'edit-csrfToken'
CSRF_TOKEN_MISSING = 'No CSRF Token found'
SESSION_LIMIT_FORM_ID = '#session-limit-page'
LOGIN_FORM_ID = '#new_login_form'
LOGOUT_BUTTON_CLASS = '.logout-link'
EMPTY_AUTH_DATA_MSG = 'Username/Password field cannot be left blank.'
SESSION_LIMIT_MSG = 'Session limit exceeded!'
INCORRECT_CREDS_MSG = 'Incorrect Credentials!'
LOGIN_SUCCESS_MSG = 'Successfully logged in!'
LOGOUT_SUCCESS_MSG = 'Successfully logged out!'


def is_logged_in(resp):
    return not bool(resp.html.find(LOGIN_FORM_ID))


def get_form_url(rhtml):
    form = rhtml.find(SESSION_LIMIT_FORM_ID, first=True)
    return form and form.element.action


def get_other_active_sessions(rhtml):
    form = rhtml.find(SESSION_LIMIT_FORM_ID, first=True)
    inputs = form.find('input')
    inputs = inputs[:-5] + inputs[-4:]
    return {inp.element.name: dict(inp.element.items()).get('value', '') for inp in inputs}


def disconnect_active_sessions(session, login_resp_html):
    token = get_csrf_token(login_resp_html, CSRF_TOKEN_INPUT_ID)
    post_url = get_form_url(login_resp_html)
    other_active_sessions = get_other_active_sessions(login_resp_html)

    resp = request(
        session=session, method='POST', url=post_url, data=other_active_sessions, token=token)
    if resp and hasattr(resp, 'status_code') and resp.status_code == 200:
        return [{'data': LOGIN_SUCCESS_MSG}]
    return [{'code': 503}]


def save_session_cookies(session, username):
    session.cookies.set_cookie(init_session_cookie("username", username))
    session.cookies.clear('www.codechef.com', '/', 'login_logout')
    session.cookies.save(ignore_expires=True, ignore_discard=True)


def make_login_req(username, password, disconnect_sessions):
    with HTMLSession() as session:
        set_session_cookies(session)

        resp = request(session=session)
        token = get_csrf_token(resp.html, CSRF_TOKEN_INPUT_ID)
        if not token:
            return [{'resps': CSRF_TOKEN_MISSING, 'code': 500}]

        data = {
            'name': username,
            'pass': password,
            'form_id': LOGIN_FORM_ID[1:],
            'csrfToken': token
        }

        resp = request(session=session, method='POST', data=data)
        resp_html = resp.html

        if resp.status_code == 200:
            if resp_html.find(SESSION_LIMIT_FORM_ID):
                if disconnect_sessions:
                    disconnect_active_sessions(session, resp_html)
                    save_session_cookies(session, username)
                    return [{'data': LOGIN_SUCCESS_MSG}]
                else:
                    logout(session=session)
                    return [{'data': SESSION_LIMIT_MSG, 'code': 400}]
            elif resp_html.find(LOGOUT_BUTTON_CLASS):
                save_session_cookies(session, username)
                return [{'data': LOGIN_SUCCESS_MSG}]
            return [{'data': INCORRECT_CREDS_MSG, 'code': 400}]
        elif resp.status_code == 503:
            return [{'code': 503}]


def login(username=None, password=None, disconnect_sessions=False):
    if not username:
        username = input('Username: ')
    if not password:
        password = getpass()

    if username and password:
        return make_login_req(username, password, disconnect_sessions)
    return [{'data': EMPTY_AUTH_DATA_MSG, 'code': 400}]


@login_required
def logout(session=None):
    resp = request(session=session, url='/logout')
    if resp.status_code == 200:
        if os.path.exists(COOKIES_FILE_PATH):
            os.remove(COOKIES_FILE_PATH)
        return [{'data': LOGOUT_SUCCESS_MSG}]
    return [{'code': 503}]
