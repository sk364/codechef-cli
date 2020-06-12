import unittest

from codechefcli import __main__ as entry_point
from codechefcli.auth import login, logout
from codechefcli.helpers import get_session
from codechefcli.utils.constants import (EMPTY_AUTH_DATA_MSG,
                                         INCORRECT_CREDS_MSG,
                                         LOGIN_SUCCESS_MSG, LOGOUT_SUCCESS_MSG,
                                         SESSION_LIMIT_MSG)

TEST_USERNAME = 'yesnoyes'
TEST_PASSWORD = 'abcdabcd'


class ScriptTests(unittest.TestCase):
    def test_main(self):
        """
        :desc: Test to check if `__main__.main` method is behaving
               correctly when receiving incorrect number of arguments.
        """

        with self.assertRaises(SystemExit):
            entry_point.main(['codechefcli', '--problem'])

    def test_create_parser(self):
        """
        :desc: Test to check if a valid parser object is returned or
               not by `__main__.create_parser` method.
        """

        parser = entry_point.create_parser()
        args = parser.parse_args(['--problem', 'WEICOM'])
        self.assertEqual(args.problem, 'WEICOM')


class LoginTests(unittest.TestCase):
    def setUp(self):
        logout()

    def test_empty_auth_data(self):
        """
        :desc: Test to check if correct data and code is returned
               when user provides empty authorization data.
        """

        username = ''
        password = ''

        resps = login(username, password, False)
        self.assertEqual(resps[0]['data'], EMPTY_AUTH_DATA_MSG)
        self.assertEqual(resps[0]['code'], 400)

    def test_correct_auth_data(self):
        """
        :desc: Test to check if correct data and code is returned
               when user provides correct authorization data.
        """

        resps = login(TEST_USERNAME, TEST_PASSWORD, False)
        self.assertEqual(resps[0]['data'], LOGIN_SUCCESS_MSG)

        # absence of code in response indicates code=200
        self.assertEqual(resps[0].get('code'), None)

    def test_incorrect_auth_data(self):
        """
        :desc: Test to check if correct data and code is returned
               when user provides incorrect authorization data.
        """

        username = 'nothing'
        password = 'nothing'

        resps = login(username, password, False)
        self.assertEqual(resps[0]['data'], INCORRECT_CREDS_MSG)
        self.assertEqual(resps[0]['code'], 400)

    def test_session_limit_exceeded(self):
        """
        :desc: Test to check `disconnect_session` argument in `login` method.
        """

        # Log a user in forcefully to further check if `disconnect_session`
        # flag works or not.
        login(TEST_USERNAME, TEST_PASSWORD, True)

        resps = login(TEST_USERNAME, TEST_PASSWORD, False)
        self.assertEqual(resps[0]['data'], SESSION_LIMIT_MSG)
        self.assertEqual(resps[0]['code'], 400)

        resps = login(TEST_USERNAME, TEST_PASSWORD, True)
        self.assertEqual(resps[0]['data'], LOGIN_SUCCESS_MSG)
        self.assertEqual(resps[0].get('code'), None)


class LogoutTests(unittest.TestCase):
    def test_logout(self):
        """
        :desc: Test to check `logout` method successfully logs out a user.
        """

        login(TEST_USERNAME, TEST_PASSWORD, True)

        resps = logout()
        self.assertEqual(resps[0]['data'], LOGOUT_SUCCESS_MSG)
        self.assertEqual(resps[0].get('code'), None)

    def test_unauthorized_logout(self):
        """
        :desc: Test to check if 401 code is returned if unauthorized.
        """

        resps = logout()

        # This implies a code of 401
        self.assertEqual(resps[0].get('data'), None)
        self.assertEqual(resps[0]['code'], 401)

    def test_logout_from_existing_session(self):
        """
        :desc: Test to check if user is logged out successfully
               from an existing session.
        """

        login(TEST_USERNAME, TEST_PASSWORD, True)
        session = get_session()

        resps = logout(session=session)
        self.assertEqual(resps[0]['data'], LOGOUT_SUCCESS_MSG)
        self.assertEqual(resps[0].get('code'), None)
