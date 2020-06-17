from unittest import TestCase

from _pytest.monkeypatch import MonkeyPatch

from codechefcli import problems
from codechefcli.problems import (get_contest_problems, get_contests,
                                  get_description, get_ratings, get_solution,
                                  get_solutions, get_tags, search_problems,
                                  submit_problem)
from tests.utils import MockHTMLResponse


class ProblemsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_get_problem_desc_invalid_json(self):
        """Should return 503 when response is not JSON-parsable"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json="{")
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_description("a", "b")[0]['code'], 503)

    def test_get_problem_desc_err(self):
        """Should return 404 when problem api returns error status"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{"status": "error"}')
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_description("a", "b")
        self.assertEqual(resps[0]['code'], 404)

    def test_get_problem_desc_success(self):
        """Should return 404 when problem api returns error status"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(
                json='{"status": "success", "problem_name": "a a", "body": "vbbv"}')
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_description("a", "b")
        self.assertEqual(
            resps[0]['data'],
            '\n\x1b[1mName: \x1b[0ma a\n\x1b[1mDescription:\x1b[0m\nvbbv\n\n\x1b[1mAuthor: \x1b[0m'
            '\n\x1b[1mDate Added: \x1b[0m\n\x1b[1mMax Time Limit: \x1b[0m secs\n\x1b[1mSource Limit'
            ': \x1b[0m Bytes\n\x1b[1mLanguages: \x1b[0m\n'
        )

    def test_submit_problem_no_login(self):
        pass

    def test_submit_problem_invalid_lang(self):
        pass

    def test_submit_problem_sol_file_not_found(self):
        pass

    def test_submit_problem_status_not_200(self):
        pass

    def test_submit_problem_invalid_status_json(self):
        pass

    def test_submit_problem_compile_err(self):
        pass

    def test_submit_problem_runtime_err(self):
        pass

    def test_submit_problem_wrong_ans(self):
        pass

    def test_submit_problem_accepted_ans(self):
        pass

    def test_submit_problem_with_status_table(self):
        pass


class SearchTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()


class TagsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()


class RatingsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()


class SolutionsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()
