from unittest import TestCase

from _pytest.monkeypatch import MonkeyPatch

from codechefcli import problems
from codechefcli.problems import (INVALID_SOLUTION_ID_MSG, LANGUAGE_SELECTOR,
                                  PAGE_INFO_CLASS, SOLUTION_ERR_MSG_CLASS,
                                  build_request_params, get_contest_problems,
                                  get_contests, get_description, get_ratings,
                                  get_solution, get_solutions, get_tags,
                                  search_problems, submit_problem)
from tests.utils import HTML, MockHTMLResponse


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

    def test_search_problems_status_not_200(self):
        """Should return 503 response code when req status is not 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(status_code=400)
        self.monkeypatch.setattr(problems, 'request', mock_req)
        self.assertEqual(search_problems("Name", "asc", "easy")[0]['code'], 503)

    def test_search_problems_success(self):
        """Should return tabular response when status code 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(data='<table></table><table> \
                <tr><th>AA</th><th>BB</th> \
                <tr><td>a1</td><td>b1</td> \
                <tr><td>a2</td><td>b2</td> \
            </table>')
        self.monkeypatch.setattr(problems, 'request', mock_req)
        self.assertEqual(
            search_problems("AA", "asc", "easy")[0]['data'],
            [['AA', 'BB', 'A1', 'B1', 'A2', 'B2'], ['a1', 'b1', 'a2', 'b2'], ['a2', 'b2']]
        )

    def test_contest_problems_invalid_json(self):
        """Should return 503 response when invalid json is received"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json="{")
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_contest_problems("AA", "asc", "CC1")[0]['code'], 503)

    def test_contest_problems_api_error(self):
        """Should return 404 response when api response status is error"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{"status": "error"}')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_contest_problems("AA", "asc", "CC1")[0]['code'], 404)

    def test_contest_problems(self):
        """Should return contest problems info and table when status is success"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{ \
                "status": "success", \
                "name": "P1", \
                "announcements": "---", \
                "problems": { \
                    "p1": { \
                        "name": "P1", \
                        "code": "p1", \
                        "problem_url": "/p1", \
                        "successful_submissions": 12, \
                        "accuracy": "11", \
                        "category_name": "main" \
                    }, \
                    "p2": { \
                        "name": "P2", \
                        "code": "p2", \
                        "problem_url": "/p2", \
                        "successful_submissions": 14, \
                        "accuracy": "1", \
                        "category_name": "" \
                    } \
                } \
            }')
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_contest_problems("Name", "asc", "CC1")
        self.assertEqual(resps[0]['data'], '\n\x1b[1mName:\x1b[0m P1\n')
        self.assertEqual(
            resps[1]['data'], [
                ['NAME', 'CODE', 'URL', 'SUCCESSFUL SUBMISSIONS', 'ACCURACY', 'SCORABLE?'],
                ['P1', 'p1', 'https://www.codechef.com/p1', 12, '11 %', 'Yes'],
                ['P2', 'p2', 'https://www.codechef.com/p2', 14, '1 %', 'No']
            ]
        )
        self.assertEqual(resps[1]['data_type'], "table")
        self.assertEqual(resps[2]['data'], "\n\x1b[1mAnnouncements\x1b[0m:\n---")


class TagsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_get_tags_invalid_json(self):
        """Should return 503 response when invalid json is received"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_tags("a", "asc", [])[0]['code'], 503)

    def test_get_tags_status_not_200(self):
        """Should return 503 response when status code is not 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{"a": "A"}', status_code=400)
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_tags("a", "asc", [])[0]['code'], 503)

    def test_get_tags(self):
        """Should return tags matrix"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(
                json='[{"tag": "t1"}, {"tag": "t2"}, \
                {"tag": "t3"}, {"tag": "t4"}, {"tag": "t5"}, {"tag": "t6"}]')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(
            get_tags("a", "asc", [])[0]['data'], [['t1', 't2', 't3', 't4', 't5'], ['t6']])

    def test_get_tagged_problems_invalid_json(self):
        """Should return 503 response when invalid json is received"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_tags("a", "asc", ["t1"])[0]['code'], 503)

    def test_get_tagged_problems_status_not_200(self):
        """Should return 503 response when status code is not 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{"a": "A"}', status_code=400)
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_tags("a", "asc", ["t1"])[0]['code'], 503)

    def test_get_tagged_problems_no_data(self):
        """Should return table with tagged problems"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{"all_problems": null}')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_tags("a", "asc", ["t1"])[0]['code'], 404)

    def test_get_tagged_problems(self):
        """Should return table with tagged problems"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{ \
                "all_problems": { \
                    "p1": {"code": "p1", "name": "P1", "attempted_by": 3, "solved_by": 2}, \
                    "p2": {"code": "p2", "name": "P2", "attempted_by": 4, "solved_by": 4} \
                } \
            }')
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_tags("Name", "asc", ["t1"])
        self.assertEqual(resps[0]['data_type'], "table")
        self.assertEqual(
            resps[0]['data'], [
                ['CODE', 'NAME', 'SUBMISSION', 'ACCURACY'],
                ['p1', 'P1', '3', '66'],
                ['p2', 'P2', '4', '100']
            ]
        )


class RatingsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_get_ratings_status_not_200(self):
        """Should return 503 response when status code is not 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(status_code=400)
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_ratings("a", "a", "a", "a", "a", "a", "a")[0]['code'], 503)

    def test_get_ratings_invalid_json(self):
        """Should return 503 response when invalid json is received"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_ratings("a", "a", "a", "a", "a", "a", "a")[0]['code'], 503)

    def test_get_ratings_null_list(self):
        """Should return 404 response code when `list` key value has no elements"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{"list": null}')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_ratings("a", "a", "a", "a", "a", "a", "a")[0]['code'], 404)

    def test_get_ratings(self):
        """Should return table containing ratings"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(json='{ \
                "list": [{ \
                    "global_rank": 1, \
                    "country_rank": 1, \
                    "username": "u1", \
                    "rating": 1, \
                    "diff": 2 \
                }] \
            }')
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_ratings("RATING", "asc", "a", "a", "a", "a", "a")
        self.assertEqual(resps[0]['data_type'], "table")
        self.assertEqual(resps[0]['data'], [
            ['GLOBAL(COUNTRY)', 'USER NAME', 'RATING', 'GAIN/LOSS'], ['1 (1)', 'u1', '1', '2']])


class ContestsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_get_contests_status_not_200(self):
        """Should return 503 response when status code is not 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(status_code=400)
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_contests(False)[0]['code'], 503)

    def test_get_contests_no_past(self):
        """Should return present & future contests"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(data="<table></table> \
                <table> \
                    <tr><th>A</th><th>B</th></tr> \
                    <tr><td>a1</td><td>b1</td></tr> \
                </table> \
                <table> \
                    <tr><th>Af</th><th>Bf</th></tr> \
                    <tr><td>af1</td><td>bf1</td></tr> \
                </table> \
            ")
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_contests(False)
        self.assertEqual(resps[0]['data'], "\x1b[1mPresent Contests:\n\x1b[0m")
        self.assertEqual(resps[1]['data_type'], "table")
        self.assertEqual(resps[1]['data'], [['A', 'B'], ['a1', 'b1']])
        self.assertEqual(resps[2]['data'], "\x1b[1mFuture Contests:\n\x1b[0m")
        self.assertEqual(resps[3]['data_type'], "table")
        self.assertEqual(resps[3]['data'], [['AF', 'BF'], ['af1', 'bf1']])

    def test_get_contests_show_past(self):
        """Should return past contests"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(data="<table></table> \
                <table> \
                    <tr><th>A</th><th>B</th></tr> \
                    <tr><td>a1</td><td>b1</td></tr> \
                </table> \
            ")
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_contests(True)
        self.assertEqual(resps[0]['data'], '\x1b[1mPast Contests:\n\x1b[0m')
        self.assertEqual(resps[1]['data_type'], "table")
        self.assertEqual(resps[1]['data'], [['A', 'B'], ['a1', 'b1']])


class SolutionsTestCase(TestCase):
    def setUp(self):
        self.monkeypatch = MonkeyPatch()

    def test_get_solutions_status_not_200(self):
        """Should return 503 response when status code is not 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(status_code=400)
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_solutions("a", "a", "a", "a", "a", "a", "a")[0]['code'], 503)

    def test_get_solutions_invalid_problem(self):
        """Should return 404 response when problem code is invalid"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(url='/p2')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_solutions("A", "asc", "p1", 1, None, None, None)[0]['code'], 404)

    def test_get_solutions_no_filters(self):
        """Should return solutions of the problem (no filters)"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(url='/p1', data='<table></table><table></table><table> \
                <tr><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr> \
                <tr><td>a1</td><td>b1</td><td>c1</td><td>d1</td><td>e1</td></tr> \
            </table>')
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_solutions("A", "asc", "p1", 1, None, None, None)
        self.assertEqual(resps[0]['data_type'], "table")
        self.assertEqual(resps[0]['data'], [['A', 'B', 'C', 'D'], ['a1', 'b1', 'c1', 'd1']])

    def test_get_solutions_no_filters_with_page_info(self):
        """Should return solutions of the problem with page info (no filters)"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(url='/p1', data=f'<table></table><table></table><table> \
                <tr><th>A</th><th>B</th><th>C</th><th>D</th><th>E</th></tr> \
                <tr><td>a1</td><td>b1</td><td>c1</td><td>d1</td><td>e1</td></tr> \
            </table><div class="{PAGE_INFO_CLASS[1:]}">111</div>')
        self.monkeypatch.setattr(problems, "request", mock_req)
        resps = get_solutions("A", "asc", "p1", 1, None, None, None)
        self.assertEqual(resps[0]['data_type'], "table")
        self.assertEqual(resps[0]['data'], [['A', 'B', 'C', 'D'], ['a1', 'b1', 'c1', 'd1']])
        self.assertEqual(resps[0]['extra'], '\nPage: 111')

    def test_build_solution_filters(self):
        """Should return params dict containing solution filters"""
        params = build_request_params(
            HTML(html=f"<select id='{LANGUAGE_SELECTOR[1:]}'> \
                <option value='a'>a</option> \
                <option value='b'>b</option> \
                <option value='c'>c</option> \
            </select>'"), "a", "WA", "abcd", 2
        )
        self.assertEqual(
            params, {'language': 'a', 'page': 1, 'status': 14, 'handle': 'abcd'})

    def test_get_solution_status_not_200(self):
        """Should return 503 response when status code is not 200"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(status_code=400)
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_solution("a")[0]['code'], 503)

    def test_get_solution_not_found(self):
        """Should return 404 response when solution not found"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(
                data=f'<div class="{SOLUTION_ERR_MSG_CLASS[1:]}">{INVALID_SOLUTION_ID_MSG}</div>')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_solution("a")[0]['code'], 404)

    def test_get_solution(self):
        """Should return solution text"""
        def mock_req(*args, **kwargs):
            return MockHTMLResponse(data=f'<pre>print("hello cc")</pre>')
        self.monkeypatch.setattr(problems, "request", mock_req)
        self.assertEqual(get_solution("a")[0]['data'], '\nprint("hello cc")\n')
