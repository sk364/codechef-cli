from http.cookiejar import Cookie
from unittest import TestCase

from requests_html import HTML, HTMLSession

from codechefcli.helpers import (SERVER_DOWN_MSG, UNAUTHORIZED_MSG, get_csrf_token, get_session,
                                 get_username, html_to_list, init_session_cookie, print_response,
                                 print_table)
from tests.utils import fake_login, fake_logout


class HelpersTestCase(TestCase):
    def test_get_session_cookies(self):
        """Should return requests_html.HTMLSession instance preloaded with cookies"""
        fake_login()

        session = get_session()
        self.assertIsInstance(session, HTMLSession)
        self.assertTrue(len(session.cookies) > 0)

    def test_get_session_no_cookies(self):
        """Should return requests_html.HTMLSession instance"""
        fake_logout()

        session = get_session()
        self.assertIsInstance(session, HTMLSession)
        self.assertEqual(len(session.cookies), 0)

    def test_init_session_cookie(self):
        """Should return cookiejar.Cookie instance with name and value as provided"""
        cookie = init_session_cookie("u", "u")
        self.assertIsInstance(cookie, Cookie)
        self.assertEqual(cookie.name, "u")
        self.assertEqual(cookie.value, "u")

    def test_get_username_not_exists(self):
        """Should return None when username not found in session cookies"""
        fake_logout()
        self.assertIsNone(get_username())

    def test_get_username_exists(self):
        """Should return None when username not found in session cookies"""
        fake_login(init_cookies=[{"name": "username", "value": "abcd"}])
        self.assertEqual(get_username(), "abcd")

    def test_html_to_list_none_html(self):
        """Should return empty list when no html is provided"""
        self.assertTrue(len(html_to_list(None)) == 0)

    def test_html_to_list_valid_html(self):
        """Should convert requests_html.HTML instance to `list`"""
        html = HTML(html=" \
            <tr><th>A</th><th>V</th></tr> \
            <tr><td>a1</td><td>v1</td></tr> \
            <tr><td>a2</td><td>v2</td></tr> \
        ")
        self.assertEqual(html_to_list(html), [['A', 'V'], ['a1', 'v1'], ['a2', 'v2']])

    def test_print_table_no_rows(self):
        """Should return None when empty list of rows is passed"""
        self.assertIsNone(print_table([]))

    def test_print_table(self):
        """Should return table string to be printed"""
        self.assertEqual(
            print_table([['A', 'V'], ['a1', 'v1'], ['a2', 'v2']], is_pager=False),
            'A    V    \n\na1   v1   \n\na2   v2   '
        )

    def test_print_response_503(self):
        """Should set color 'FAIL' and data when 503 code is provided"""
        self.assertEqual(print_response(code=503)[0], f'\x1b[91m{SERVER_DOWN_MSG}\x1b[0m')

    def test_print_response_404_400(self):
        """Should set color 'WARNING' when code is 404 / 400"""
        self.assertEqual(print_response(code=404, data='a')[0], '\x1b[93ma\x1b[0m')
        self.assertEqual(print_response(code=400, data='a')[0], '\x1b[93ma\x1b[0m')

    def test_print_response_401(self):
        """Should set color 'FAIL' and data when 401 code is provided"""
        self.assertEqual(print_response(code=401)[0], f'\x1b[91m{UNAUTHORIZED_MSG}\x1b[0m')

    def test_print_response_table(self):
        """Should set is_pager True when data_type table is provided with no pager in kwargs"""
        self.assertEqual(print_response(data_type='table', data=[['1', '2']])[0], '1   2   ')

    def test_print_response_no_data_no_extra(self):
        """Should return no data msg"""
        self.assertEqual(print_response()[0], '\x1b[93mNothing to show.\x1b[0m')

    def test_print_response_no_data(self):
        """Should return no data msg"""
        self.assertIsNone(print_response(extra='a')[0])

    def test_get_csrf_token_no_token(self):
        """Should return None when token not found in html"""
        html = HTML(html="<html></html>")
        self.assertIsNone(get_csrf_token(html, "a"))

    def test_get_csrf_token_no_value(self):
        """Should return None when html element has no value"""
        html = HTML(html="<input id='a' />")
        self.assertIsNone(get_csrf_token(html, "a"))

    def test_get_csrf_token(self):
        """Should return token from html element's value"""
        html = HTML(html="<input id='a' value='b' />")
        self.assertEqual(get_csrf_token(html, "a"), 'b')
