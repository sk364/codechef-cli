from unittest import TestCase

from _pytest.monkeypatch import MonkeyPatch

from codechefcli import teams
from tests.utils import MockHTMLResponse


class TeamsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_get_team_no_name(self):
        """Should return empty list response when empty name is given"""
        self.assertEqual(teams.get_team(None), [])

    def test_get_team_status_not_200(self):
        """Should return 503 response code on any other status than 200 and 404"""
        def mock_req_team(*args, **kwargs):
            return MockHTMLResponse(status_code=500)
        self.monkeypatch.setattr(teams, "request", mock_req_team)
        self.assertEqual(teams.get_team("abcd")[0]["code"], 503)

    def test_get_team_status_404(self):
        """Should return 404 response code on 404 status code"""
        def mock_req_team(*args, **kwargs):
            return MockHTMLResponse(status_code=404)
        self.monkeypatch.setattr(teams, "request", mock_req_team)
        resps = teams.get_team("abcd")
        self.assertEqual(resps[0]["code"], 404)
        self.assertEqual(resps[0]["data"], "Team not found.")

    def test_get_team(self):
        """Should return team info"""
        def mock_req_team(*args, **kwargs):
            return MockHTMLResponse(data="<table></table><table><h1>ABCD</h1></table><table> \
                <tr><td>A:</td><td>C</td></tr> \
                <tr><td>B:</td><td>D</td></tr> \
                <tr><td>E:</td><td>F</td></tr> \
                <tr><td>Information for G:</td><td>G</td></tr> \
                <tr><td>xx</td></tr> \
            </table><table> \
                <tr><td>T</td><td>U</td></tr> \
                <tr><td>t1</td><td>u1</td></tr> \
                <tr><td>t2</td><td>u2</td></tr>\
            </table>")
        self.monkeypatch.setattr(teams, "request", mock_req_team)
        resps = teams.get_team("abcd")
        self.assertEqual(
            resps[0]["data"],
            '\nABCD\n\nA: C\nB: D\nE: F\n\nInformation for G: G\n\nProblems Successfully Solved:\n'
        )
        self.assertListEqual(resps[1]["data"], [['T', 'U'], ['t1', 'u1'], ['t2', 'u2']])
