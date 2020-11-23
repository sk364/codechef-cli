import os
from getpass import getpass

from requests_html import HTMLSession

from codechefcli.decorators import login_required
from codechefcli.helpers import (COOKIES_FILE_PATH, CSRF_TOKEN_INPUT_ID, get_csrf_token,
                                 init_session_cookie, request, set_session_cookies)

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
    """Checks if the user is logged in or not"""
    return not bool(resp.html.find(LOGIN_FORM_ID))


def get_form_url(rhtml):
    """Returns the url for the session limit page"""
    form = rhtml.find(SESSION_LIMIT_FORM_ID, first=True)
    return form and form.element.action


def get_other_active_sessions(rhtml):
    """Returns other active sessions of user other than the current one

    Args:
      rhtml: html string from where active session info is to be extracted.

    Returns:
      dictionary containing information about other active sessions
    """
    form = rhtml.find(SESSION_LIMIT_FORM_ID, first=True)
    inputs = form.find('input')
    inputs = inputs[:-5] + inputs[-4:]
    return {inp.element.name: dict(inp.element.items()).get('value', '') for inp in inputs}


def disconnect_active_sessions(session, login_resp_html):
    """Disconnects the users all active sessions other than the current session.

    Args:
      session:
        An HTMLSession object representing the current session of user
      login_resp_html:
        HTML response from where user has to disconnect active sessions

    Returns:
      [{'data': 'Successfully logged in!'}] if previous sessions were closed and
      user was Successfully logged in.
      ['code': 503] otherwise indicating that the service was not available.
      Possible causes could be that the server was not ready, or is down for
      maintanance or was overloaded
    """
    token = get_csrf_token(login_resp_html, CSRF_TOKEN_INPUT_ID)
    post_url = get_form_url(login_resp_html)
    other_active_sessions = get_other_active_sessions(login_resp_html)

    resp = request(
        session=session, method='POST', url=post_url, data=other_active_sessions, token=token)
    if resp and hasattr(resp, 'status_code') and resp.status_code == 200:
        return [{'data': LOGIN_SUCCESS_MSG}]
    return [{'code': 503}]


def save_session_cookies(session, username):
    """Saves cookies for current user session

    Args:
      session:
        An HTMLSession object representing the current session of user
      username:
        username for CodeChef account
    """
    session.cookies.set_cookie(init_session_cookie("username", username))
    session.cookies.clear('www.codechef.com', '/', 'login_logout')
    session.cookies.save(ignore_expires=True, ignore_discard=True)


def make_login_req(username, password, disconnect_sessions):
    """Makes a request to the codeChef site to log into your account.

    This method uses the username and password supplied to it to login to CodeChef.
    If multiple sessions are open on other devices with the same credentials,
    it closes these sessions based on the disconnect_sessions parameter.

    Args:
      username:
        string containing the username for CodeChef account
      password:
        string containing the password for CodeChef account
      disconnect_sessions:
        boolean value indicating whether user wants to disconnect other open
        sessions or log out from current session

    Returns:
      List of dictionaries containing a message whether the operation was
      successful or any errors that occurred, and the http response code for
      the operation.

      [{"data": "\nBye."}]
      [{'data': 'Username/Password field cannot be left blank.', 'code': 400}]

    """
    with HTMLSession() as session:
        set_session_cookies(session)

        resp = request(session=session)
        token = get_csrf_token(resp.html, CSRF_TOKEN_INPUT_ID)
        if not token:
            return [{'data': CSRF_TOKEN_MISSING, 'code': 500}]

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
                    resps = disconnect_active_sessions(session, resp_html)
                    save_session_cookies(session, username)
                    return resps
                else:
                    logout(session=session)
                    return [{'data': SESSION_LIMIT_MSG, 'code': 400}]
            elif resp_html.find(LOGOUT_BUTTON_CLASS):
                save_session_cookies(session, username)
                return [{'data': LOGIN_SUCCESS_MSG}]
            return [{'data': INCORRECT_CREDS_MSG, 'code': 400}]
        return [{'code': 503}]


def login(username=None, password=None, disconnect_sessions=False):
    """Logs in to the users CodeChef account.

    Uses the optional username and password paramters to log into the users
    account. If no paramters are passed, prompts the user to input them.

    Args:
      username:
        Username for CodeChef account. If no value is passed, it prompts the
        user to enter it.
      password:
        password for CodeChef account. If no value is passed, it prompts the
        user to enter it.
      disconnect_sessions:
        True or False value depending on whether user wants to disconnect from
        their previous sessions from other devices.

    Returns:
      List of dictionaries containing a message whether the operation was
      successful or any errors that occurred, and the http response code for
      the operation.

      [{"data": "\nBye."}]
      [{'data': 'Username/Password field cannot be left blank.', 'code': 400}]

    """
    if username is None:
        username = input('Username: ')
    if password is None:
        password = getpass()

    if username and password:
        return make_login_req(username, password, disconnect_sessions)
    return [{'data': EMPTY_AUTH_DATA_MSG, 'code': 400}]


@login_required
def logout(session=None):
    """Logs the user out of the current session.

    It first checks if the user has logged into his account, by consulting the
    cookies. Then logs out the user.

    Args:
      session: HTMLSession object for the current session

    Returns:
      [{'data': 'Successfully logged out!'}] if user was successfull logged out
      ['code': 503] otherwise indicating that the service was not available.
      Possible causes could be that the server was not ready, or is down for
      maintanance or was overloaded
    """
    resp = request(session=session, url='/logout')
    if resp.status_code == 200:
        if os.path.exists(COOKIES_FILE_PATH):
            os.remove(COOKIES_FILE_PATH)
        return [{'data': LOGOUT_SUCCESS_MSG}]
    return [{'code': 503}]
