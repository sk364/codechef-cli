from unittest import TestCase

from _pytest.monkeypatch import MonkeyPatch

from codechefcli import users
from codechefcli.users import (HEADER, RATING_NUMBER_CLASS, RATING_RANKS_CLASS,
                               STAR_RATING_CLASS, USER_DETAILS_CLASS,
                               USER_DETAILS_CONTAINER_CLASS, get_user)
from tests.utils import MockHTMLResponse


class UsersTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_get_user_empty_username(self):
        """Should return empty list response"""
        self.assertEqual(get_user(None), [])

    def test_get_user_status_not_200(self):
        """Should return 503 response on any status code other than 200"""
        def mock_req_user(*args, **kwargs):
            return MockHTMLResponse(status_code=403)
        self.monkeypatch.setattr(users, "request", mock_req_user)

        resps = get_user("abc")
        self.assertEqual(resps[0]["code"], 503)

    def test_get_user_team_name(self):
        """Should return 400 response when username is of a team name"""
        def mock_req_user(*args, **kwargs):
            return MockHTMLResponse(url="/teams/view/abcd")
        self.monkeypatch.setattr(users, "request", mock_req_user)

        name = "abcd"
        resps = get_user(name)

        self.assertEqual(resps[0]["code"], 400)
        self.assertTrue(f'--team {name}' in resps[0]["data"])

    def test_get_user_not_found(self):
        """Should return 404 when the user is not found i.e. resp url is base url"""
        def mock_req_user(*args, **kwargs):
            return MockHTMLResponse()
        self.monkeypatch.setattr(users, "request", mock_req_user)

        resps = get_user("abcd")
        self.assertEqual(resps[0]["code"], 404)
        self.assertEqual(resps[0]["data"], "User not found.")

    def test_get_user(self):
        """Should return user info"""
        def mock_req_user(*args, **kwargs):
            return MockHTMLResponse(data=f"<div class='{USER_DETAILS_CONTAINER_CLASS[1:]}'> \
                <{HEADER}>ABCD's Profile</{HEADER}> \
                <div class='{USER_DETAILS_CLASS[1:]}'> \
                    <li>aa: 1</li> \
                    <li>bb: 2</li> \
                    <li>cc: 3</li> \
                    <li>dd: 4</li> \
                </div> \
                <div class='{STAR_RATING_CLASS[1:]}'>3star</div> \
            </div> \
            <div class='{RATING_NUMBER_CLASS[1:]}'>1111</div> \
            <div class='{RATING_RANKS_CLASS[1:]}'> \
                <li><a>123</a></li> \
                <li><a>11</a></li> \
            </div>", url="/users/abcd/")
        self.monkeypatch.setattr(users, "request", mock_req_user)

        resps = get_user("abcd")
        self.assertEqual(
            resps[0]["data"],
            "\n\x1b[1mUser Details for ABCD's Profile (abcd):\x1b[0m\n\nbb: 2\ncc: 3\n"
            "User's Teams: https://www.codechef.com/users/abcd/teams/\n\nRating: 3star 1111\nGlobal"
            " Rank: 123\nCountry Rank: 11\n\nFind more at: https://www.codechef.com/users/abcd/\n"
        )
