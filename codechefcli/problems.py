import math
import re

from requests_html import HTML

from codechefcli.auth import is_logged_in
from codechefcli.decorators import login_required, sort_it
from codechefcli.helpers import (BASE_URL, SERVER_DOWN_MSG, get_csrf_token,
                                 html_to_list, request, style_text)

CSRF_TOKEN_SUBMIT_FORM = "edit-csrfToken"
LANGUAGE_SELECTOR = "#language"
INVALID_PROBLEM_CODE_MSG = 'Invalid Problem Code.'
PAGE_INFO_CLASS = '.pageinfo'
PROBLEM_SUBMISSION_FORM_ID = '#problem-submission'
PROBLEM_SUB_DATA_FORM_ID = 'problem_submission'
PROBLEM_SUBMISSION_INPUT_ID = '#edit-problem-submission-form-token'
LANGUAGE_DROPDOWN_ID = '#edit-language'
COMPILATION_ERROR_CLASS = '.cc-error-txt'
PROBLEM_LIST_TABLE_HEADINGS = ['CODE', 'NAME', 'SUBMISSION', 'ACCURACY']
RESULT_CODES = {'AC': 15, 'WA': 14, 'TLE': 13, 'RTE': 12, 'CTE': 11}
RATINGS_TABLE_HEADINGS = ['GLOBAL(COUNTRY)', 'USER NAME', 'RATING', 'GAIN/LOSS']


def get_description(problem_code, contest_code):
    url = f'/api/contests/{contest_code}/problems/{problem_code}'
    resp = request(url=url)

    try:
        resp_json = resp.json()
    except ValueError:
        return [{'code': 503}]

    if resp_json["status"] == "success":
        problem = [
            '',
            style_text('Name: ', "BOLD") + resp_json['problem_name'],
            style_text("Description:", "BOLD"),
            re.sub(r'(<|<\/)\w+>', '', resp_json["body"]),
            '',
            style_text("Author: ", "BOLD") + resp_json['problem_author'],
            style_text("Date Added: ", "BOLD") + resp_json['date_added'],
            style_text("Max Time Limit: ", "BOLD") + f"{resp_json['max_timelimit']} secs",
            style_text("Source Limit: ", "BOLD") + f"{resp_json['source_sizelimit']} Bytes",
            style_text("Languages: ", "BOLD") + resp_json['languages_supported'],
            ''
        ]
        if resp_json.get('tags'):
            problem.append(
                style_text('Tags: ', 'BOLD') +
                " ".join([tag.text for tag in HTML(html=resp_json['tags']).find('a')])
            )
            problem.append('')
        if resp_json.get('editorial_url'):
            problem.append(style_text('Editorial: ', 'BOLD') + resp_json['editorial_url'])
            problem.append('')

        return [{"data": "\n".join(problem)}]
    elif resp_json["status"] == "error":
        return [{
            'data': 'Problem not found. Use `--search` to search in a specific contest',
            'code': 404
        }]
    return [{'code': 503}]


def get_form_token(rhtml):
    form = rhtml.find(PROBLEM_SUBMISSION_FORM_ID, first=True)
    inp = form and form.find(PROBLEM_SUBMISSION_INPUT_ID, first=True)
    input_element = inp and hasattr(inp, 'element') and inp.element
    return input_element is not None and hasattr(input_element, 'value') and input_element.value


def get_status_table(status_code):
    resp = request(url=f'/error_status_table/{status_code}')
    if resp.status_code == 200:
        if not resp.text:
            return
        return resp.html


def get_compilation_error(status_code):
    resp = request(url=f'/view/error/{status_code}')
    if resp.status_code == 200:
        return resp.html.find(COMPILATION_ERROR_CLASS, first=True).text
    return SERVER_DOWN_MSG


def get_language_code(rhtml, language):
    form = rhtml.find(PROBLEM_SUBMISSION_FORM_ID, first=True)
    languages_dropdown = form.find(LANGUAGE_DROPDOWN_ID, first=True)
    for option in languages_dropdown.find('option'):
        if language.lower() + '(' in option.text.lower():
            return dict(option.element.items())['value']


@login_required
def submit_problem(problem_code, solution_file, language):
    url = f'/submit/{problem_code}'
    get_resp = request(url=url)

    if not is_logged_in(get_resp):
        return [{"code": 401, "data": "This session has been disconnected. Login again."}]

    if get_resp.status_code == 200:
        rhtml = get_resp.html
        form_token = get_form_token(rhtml)
        language_code = get_language_code(rhtml, language)
        csrf_token = get_csrf_token(rhtml, CSRF_TOKEN_SUBMIT_FORM)

        if language_code is None:
            return [{'code': 400, 'data': 'Invalid language.'}]
    else:
        return [{'code': 503}]

    try:
        solution_file_obj = open(solution_file)
    except IOError:
        return [{'data_type': 'text', 'data': 'Solution file not found.', 'code': 400}]

    data = {
        'language': language_code,
        'problem_code': problem_code,
        'form_id': PROBLEM_SUB_DATA_FORM_ID,
        'form_token': form_token
    }
    files = {'files[sourcefile]': solution_file_obj}

    post_resp = request(method='POST', url=url, data=data, files=files)
    if post_resp.status_code == 200:
        print(style_text('Submitting code...\n', 'BLUE'))

        status_code = post_resp.url.split('/')[-1]
        url = f'/get_submission_status/{status_code}'
        print(style_text('Fetching results...\n', 'BLUE'))
        while True:
            resp = request(url=url, token=csrf_token)

            try:
                status_json = resp.json()
            except ValueError:
                continue

            result_code = status_json['result_code']

            if result_code != 'wait':
                if result_code == 'compile':
                    error_msg = get_compilation_error(status_code)
                    compile_error_msg = u'Compilation error.\n{0}'.format(error_msg)
                    data = style_text(compile_error_msg, 'FAIL')
                elif result_code == 'runtime':
                    error_msg = status_json['signal']
                    runtime_error_msg = u'Runtime error. {0}\n'.format(error_msg)
                    data = style_text(runtime_error_msg, 'FAIL')
                elif result_code == 'wrong':
                    data = style_text('Wrong answer\n', 'FAIL')
                elif result_code == 'accepted':
                    data = 'Correct answer\n'
                else:
                    data = ''

                resps = [{'data': data}]
                status_table = get_status_table(status_code)
                if status_table:
                    resps.append({'data_type': 'table', 'data': html_to_list(status_table)})
                return resps
            else:
                print(style_text('Waiting...\n', 'BLUE'))
    return [{'code': 503}]


@sort_it
def get_contest_problems(sort, order, contest_code):
    url = f'/api/contests/{contest_code}?'
    resp = request(url=url)

    try:
        resp_json = resp.json()
    except ValueError:
        return [{"code": 503}]

    if resp_json['status'] == "success":
        problems_table = [[
            x.upper() for x in [
                "Name", "Code", "URL", "Successful Submissions", "Accuracy", "Scorable?"]
        ]]
        for _, problem in resp_json['problems'].items():
            problems_table.append([
                problem['name'],
                problem['code'],
                f"{BASE_URL}{problem['problem_url']}",
                problem['successful_submissions'],
                f"{problem['accuracy']} %",
                "Yes" if problem['category_name'] == 'main' else "No"
            ])

        return [
            {'data': f"\n{style_text('Name:', 'BOLD')} {resp_json['name']}\n"},
            {'data': problems_table, "data_type": "table"},
            {'data': f'\n{style_text("Announcements", "BOLD")}:\n{resp_json["announcements"]}'}
        ]
    elif resp_json['status'] == "error":
        return [{'data': 'Contest doesn\'t exist.', 'code': 404}]
    return [{"code": 503}]


@sort_it
def search_problems(sort, order, search_type):
    url = f'/problems/{search_type.lower()}'
    resp = request(url=url)
    if resp.status_code == 200:
        return [{'data_type': 'table', 'data': html_to_list(resp.html.find('table')[1])}]
    return [{"code": 503}]


def get_tags(sort, order, tags):
    if len(tags) == 0:
        return get_all_tags()
    return get_problem_tags(sort, order, tags)


def get_all_tags():
    resp = request(url='/get/tags/problems')

    try:
        all_tags = resp.json()
    except ValueError:
        return [{'code': 503}]

    if resp.status_code == 200:
        data_rows = []
        num_cols = 5
        row = []

        for index, tag in enumerate(all_tags):
            tag_name = tag.get('tag', '')
            if len(row) < num_cols:
                row.append(tag_name)
            else:
                data_rows.append(row)
                row = [tag_name]

        return [{'data': data_rows, 'data_type': 'table'}]

    return [{'code': 503}]


@sort_it
def get_problem_tags(sort, order, tags):
    resp = request(url=f'/get/tags/problems/{",".join(tags)}')

    try:
        all_tags = resp.json()
    except ValueError:
        return [{'code': 503}]

    if resp.status_code == 200:
        data_rows = [PROBLEM_LIST_TABLE_HEADINGS]
        all_tags = all_tags['all_problems']

        if not all_tags:
            return [{'code': 404, 'extra': "Sorry, there are no problems with the following tags!"}]

        for _, problem in all_tags.items():
            problem_info = [
                problem.get('code', ''),
                problem.get('name', ''),
                str(problem.get('attempted_by', ''))
            ]
            try:
                accuracy = (problem.get('solved_by') / problem.get('attempted_by')) * 100
                problem_info.append(str(math.floor(accuracy)))
            except TypeError:
                problem_info.append('')
            data_rows.append(problem_info)

        return [{'data': data_rows, 'data_type': 'table'}]

    return [{'code': 503}]


@sort_it
def get_ratings(sort, order, country, institution, institution_type, page, lines):
    csrf_resp = request(url='/ratings/all')
    if csrf_resp.status_code == 200:
        csrf_token = get_csrf_token(csrf_resp.html, CSRF_TOKEN_SUBMIT_FORM)
    else:
        return [{'code': 503}]

    url = '/api/ratings/all?sortBy=global_rank&order=asc'
    params = {'page': str(page), 'itemsPerPage': str(lines), 'filterBy': ''}
    if country:
        params['filterBy'] += f'Country={country};'
    if institution:
        institution = institution.title()
        params['filterBy'] += f'Institution={institution};'
    if institution_type:
        params['filterBy'] += f'Institution type={institution_type};'

    resp = request(url=url, params=params, token=csrf_token)

    if resp.status_code == 200:
        try:
            ratings = resp.json()
        except ValueError:
            return [{'code': 503}]

        ratings = ratings.get('list')
        if len(ratings) == 0:
            return [{'code': 404, 'data': 'No ratings found'}]

        data_rows = [RATINGS_TABLE_HEADINGS]
        for user in ratings:
            data_rows.append([
                f"{str(user['global_rank'])} ({str(user['country_rank'])})",
                user['username'],
                str(user['rating']),
                str(user['diff'])
            ])
        return [{'code': 200, 'data': data_rows, 'data_type': 'table'}]
    return [{'code': 503}]


def get_contests(show_past):
    resp = request(url='/contests')
    if resp.status_code == 200:
        tables = resp.html.find('table')
        labels = ['Present', 'Future']
        if show_past:
            labels = ['Past']
            tables = [tables[0], tables[-1]]

        resps = []
        for idx, label in enumerate(labels):
            resps += [
                {'data': style_text(f'{label} Contests:\n', 'BOLD')},
                {'data': html_to_list(tables[idx + 1]), 'data_type': 'table'}
            ]
        return resps
    return [{'code': 503}]


def build_request_params(resp_html, language, result, username, page):
    params = {'page': page - 1} if page != 1 else {}
    if language:
        lang_dropdown = resp_html.find(LANGUAGE_SELECTOR)
        options = lang_dropdown.find('option')

        for option in options:
            if language.upper() == option.text.strip().upper():
                params['language'] = option['value']
                break
    if result:
        params['status'] = RESULT_CODES[result.upper()]
    if username:
        params['handle'] = username
    return params


@sort_it
def get_solutions(sort, order, problem_code, page, language, result, username):
    url = f'/status/{problem_code.upper()}'
    resp = request(url=url)

    params = build_request_params(resp.html, language, result, username, page)
    resp = request(url=url, params=params)

    if resp.status_code == 200:
        if problem_code in resp.url:
            resp_html = resp.html
            solution_table = resp_html.find('table')[2]
            page_info = resp_html.find(PAGE_INFO_CLASS, first=True)

            data_rows = html_to_list(solution_table)
            for row in data_rows:
                # remove view solution column
                del row[-1]

                # format result column
                row[3] = ' '.join(row[3].split('\n'))

            resp = {'data_type': 'table', 'data': data_rows}
            if page_info:
                resp['extra'] = f'\nPage: {page_info.text}'

            return [resp]
        else:
            return [{'code': 404, 'data': INVALID_PROBLEM_CODE_MSG}]
    return [{'code': 503}]


def get_solution(solution_code):
    resp = request(url=f'/viewplaintext/{solution_code}')
    if resp.status_code == 200:
        if resp.html.find('.err-message') == "Invalid solution ID":
            return [{'code': 404, "data": "Invalid Solution ID"}]
        else:
            return [{'data': f'\n{resp.html.find("pre", first=True).element.text}\n'}]
    return [{'code': 503}]
