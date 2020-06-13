import unittest

from _pytest.monkeypatch import MonkeyPatch
from requests_html import HTML

from codechefcli import __main__ as entry_point
from codechefcli import auth, problems
from codechefcli.auth import (CSRF_TOKEN_MISSING, EMPTY_AUTH_DATA_MSG,
                              INCORRECT_CREDS_MSG, LOGIN_SUCCESS_MSG,
                              LOGOUT_BUTTON_CLASS, LOGOUT_SUCCESS_MSG,
                              SESSION_LIMIT_FORM_ID, SESSION_LIMIT_MSG,
                              disconnect_active_sessions, login, logout)
from codechefcli.helpers import CSRF_TOKEN_INPUT_ID, get_session


class MockHTMLResponse:
    def __init__(self, data='<html />', status_code=200):
        self.html = HTML(html=data)
        self.status_code = status_code


class EntryPointTests(unittest.TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_main_invalid_args(self):
        """Should raise SystemExit exception on incorrect number of args for a particular option"""
        with self.assertRaises(SystemExit):
            entry_point.main(['codechefcli', '--problem'])

    def test_main_valid_args(self):
        """Should return responses when valid args are present"""
        def mock_get_desc(*args, **kwargs):
            return [{"data": "Lots of description. Some math. Some meta info. Done."}]

        self.monkeypatch.setattr(entry_point, "get_description", mock_get_desc)

        resps = entry_point.main(['codechefcli', '--problem', 'CCC'])
        self.assertEqual(resps[0]["data"], "Lots of description. Some math. Some meta info. Done.")

    def test_create_parser(self):
        """Should not explode when parser is parsing the args"""

        parser = entry_point.create_parser()
        args = parser.parse_args(['--problem', 'WEICOM'])
        self.assertEqual(args.problem, 'WEICOM')


class LoginTests(unittest.TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_empty_auth_data(self):
        """Should return empty auth data message"""
        def mock_input(*args, **kwargs):
            return ''

        auth.input = mock_input
        auth.getpass = mock_input

        resps = login(username='', password='', disconnect_sessions=False)
        self.assertEqual(resps[0]['data'], EMPTY_AUTH_DATA_MSG)
        self.assertEqual(resps[0]['code'], 400)

    def test_correct_auth_data(self):
        """Should login on correct auth data"""
        def mock_request(*args, **kwargs):
            if kwargs.get('method'):
                return MockHTMLResponse(
                    data=f'<button class="{LOGOUT_BUTTON_CLASS[1:]}">Logout</button>')
            else:
                return MockHTMLResponse(data=f"<input id='{CSRF_TOKEN_INPUT_ID}' value='ab' />")

        def mock_save_cookies(*args, **kwargs):
            pass

        self.monkeypatch.setattr(auth, 'request', mock_request)
        self.monkeypatch.setattr(auth, 'save_session_cookies', mock_save_cookies)

        resps = login(username='cc', password='cc', disconnect_sessions=False)
        self.assertEqual(resps[0]['data'], LOGIN_SUCCESS_MSG)

    def test_incorrect_auth_data(self):
        """Should return incorrect creds message"""
        def mock_request(*args, **kwargs):
            if kwargs.get('method'):
                return MockHTMLResponse(data=f'<button>Login</button>')
            else:
                return MockHTMLResponse(data=f"<input id='{CSRF_TOKEN_INPUT_ID}' value='ab' />")

        self.monkeypatch.setattr(auth, 'request', mock_request)

        resps = login(username='nope', password='nope', disconnect_sessions=False)
        self.assertEqual(resps[0]['data'], INCORRECT_CREDS_MSG)
        self.assertEqual(resps[0]['code'], 400)

    def test_no_csrf_token(self):
        """Should return csrf token missing message when there isn't one in the response html"""
        def mock_request(*args, **kwargs):
            return MockHTMLResponse(data=f"<input id='invalid-token-id' value='aaa' />")
        self.monkeypatch.setattr(auth, 'request', mock_request)

        resps = login(username='cc', password='cc', disconnect_sessions=False)
        self.assertEqual(resps[0]['data'], CSRF_TOKEN_MISSING)
        self.assertEqual(resps[0]['code'], 500)

    def test_status_code_not_200(self):
        """Should return code 503 when status code is not 200"""
        def mock_request(*args, **kwargs):
            if kwargs.get('method'):
                return MockHTMLResponse(status_code=500)
            else:
                return MockHTMLResponse(data=f"<input id='{CSRF_TOKEN_INPUT_ID}' value='ab' />")

        self.monkeypatch.setattr(auth, 'request', mock_request)

        resps = login(username='cc', password='cc', disconnect_sessions=False)
        self.assertEqual(resps[0]['code'], 503)

    def test_session_limit_exceeded_no_disconnect(self):
        """Should return session limit msg on no disconnect"""

        def mock_request(*args, **kwargs):
            if kwargs.get('method'):
                return MockHTMLResponse(data=f'<input id="{SESSION_LIMIT_FORM_ID[1:]}" />')
            else:
                return MockHTMLResponse(data=f"<input id='{CSRF_TOKEN_INPUT_ID}' value='ab' />")

        def mock_logout(*args, **kwargs):
            pass

        self.monkeypatch.setattr(auth, 'request', mock_request)
        self.monkeypatch.setattr(auth, 'logout', mock_logout)

        resps = login(username='cc', password='cc', disconnect_sessions=False)
        self.assertEqual(resps[0]['data'], SESSION_LIMIT_MSG)
        self.assertEqual(resps[0]['code'], 400)

    def test_session_limit_exceeded_disconnect(self):
        """Should disconnect active sessions and login in the current returning login success msg"""

        def mock_request(*args, **kwargs):
            if kwargs.get('method'):
                return MockHTMLResponse(data=f'<input id="{SESSION_LIMIT_FORM_ID[1:]}" />')
            else:
                return MockHTMLResponse(data=f"<input id='{CSRF_TOKEN_INPUT_ID}' value='ab' />")

        def mock_logout(*args, **kwargs):
            pass

        def mock_disconnect(*args, **kwargs):
            return [{'data': LOGIN_SUCCESS_MSG}]

        def mock_save_cookies(*args, **kwargs):
            pass

        self.monkeypatch.setattr(auth, 'request', mock_request)
        self.monkeypatch.setattr(auth, 'logout', mock_logout)
        self.monkeypatch.setattr(auth, 'disconnect_active_sessions', mock_disconnect)
        self.monkeypatch.setattr(auth, 'save_session_cookies', mock_save_cookies)

        resps = login(username='cc', password='cc', disconnect_sessions=True)
        self.assertEqual(resps[0]['data'], LOGIN_SUCCESS_MSG)

    def test_disconnect_active_sessions_success(self):
        """Should return login success msg on disconnect"""
        def mock_request(*args, **kwargs):
            return MockHTMLResponse()

        self.monkeypatch.setattr(auth, 'request', mock_request)

        inputs = "".join([f"<input name='{idx}' value='{idx}' />" for idx in range(6)])
        html = HTML(html=f'<input id="{CSRF_TOKEN_INPUT_ID}" value="ab" />'
                    f'<form id="{SESSION_LIMIT_FORM_ID[1:]}">{inputs}</form>')
        resps = disconnect_active_sessions(None, html)
        self.assertEqual(resps[0]['data'], LOGIN_SUCCESS_MSG)

    def test_disconnect_active_sessions_success(self):
        """Should return 503 when status code is not 200"""
        def mock_request(*args, **kwargs):
            return MockHTMLResponse(status_code=500)

        self.monkeypatch.setattr(auth, 'request', mock_request)

        inputs = "".join([f"<input name='{idx}' value='{idx}' />" for idx in range(6)])
        html = HTML(html=f'<input id="{CSRF_TOKEN_INPUT_ID}" value="ab" />'
                    f'<form id="{SESSION_LIMIT_FORM_ID[1:]}">{inputs}</form>')
        resps = disconnect_active_sessions(None, html)
        self.assertEqual(resps[0]['code'], 503)
