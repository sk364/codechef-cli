import math
import re
from datetime import datetime

from bs4 import BeautifulSoup

from .decorators import login_required, sort_it
from .utils.constants import (BASE_URL, DEFAULT_NUM_LINES,
                              PROBLEM_LIST_TABLE_HEADINGS,
                              RATINGS_TABLE_HEADINGS, RESULT_CODES,
                              SERVER_DOWN_MSG)
from .utils.helpers import color_text, get_session, html_to_list, request


def get_description(problem_code, contest_code=None):
    """
    :desc: Retrieves a particular problem description.
    :param: `problem_code` Code of the problem.
    :return: `str` [description / Not Found / Server down]
    """

    session = get_session()

    url = BASE_URL
    if contest_code is not None:
        url += '/' + contest_code
    url += '/problems/' + problem_code

    req_obj = request(session, 'GET', url)

    if req_obj.status_code == 200:
        problem_html = req_obj.text
        soup = BeautifulSoup(problem_html, 'html.parser')
        resps = []

        if soup.find(id='problem-code'):
            content = soup.find_all('div', class_='content')[1]
            content.find_all('h3')[0].extract()
            content.find_all('h3')[0].extract()
            while content.find('img'):
                img = content.find('img')
                img.name = "p"
                img.string  = img['src']

            problem_info_table = soup.find_all('table')[2]

            resps = [{
                'data_type': 'text',
                'code': 200,
                'data': color_text(color_text('Problem Description:', 'BOLD'), 'BLUE'),
            }, {
                'data_type': 'text',
                'code': 200,
                'data': content.text,
                'pager': True
            }, {
                'data_type': 'text',
                'code': 200,
                'data': color_text(color_text('Problem Info:', 'BOLD'), 'BLUE')
            }, {
                'data_type': 'table',
                'code': 200,
                'data': str(problem_info_table),
                'inverse': True
            }]
        else:
            resps.append({'data': 'Problem not found.', 'code': 404})
            if contest_code is None:
                resps.append({
                    'data': 'Maybe, the problem exists only in the contest.\n'
                            'Add ' + color_text("--search <contest code>", 'BOLD') +
                            ' to search in the contest specific problems.'
                })
        return resps

    elif req_obj.status_code == 503:
        return [{'code': 503}]


def get_form_token(problem_submit_html):
    """
    :desc: Retrieves problem submission form token.
    :param: `problem_submit_html` HTML text containing problem submission form.
    :return: `str` form token value
    """

    soup = BeautifulSoup(problem_submit_html, 'html.parser')
    form = soup.find('form', id='problem-submission')
    return form.find('input', id='edit-problem-submission-form-token')['value']


def get_error_table(status_code):
    """
    :desc: Retrieves error status table.
    :param: `status_code` Status code of the submitted problem.
    :return: `str` error status table
    """

    session = get_session()
    url = BASE_URL + '/error_status_table/' + status_code
    req_obj = request(session, 'GET', url)
    if req_obj.status_code == 200:
        return req_obj.text

    return None


def get_compilation_error(status_code):
    """
    :desc: Retrieves compilation error text.
    :param: `status_code` Status code of the submitted problem.
    :return: `str` Compilation error text.
    """

    session = get_session()
    url = BASE_URL + '/view/error/' + status_code
    req_obj = request(session, 'GET', url)

    if req_obj.status_code == 200:
        soup = BeautifulSoup(req_obj.text, 'html.parser')
        return soup.find('div', class_='cc-error-txt').text

    if req_obj.status_code == 503:
        return SERVER_DOWN_MSG

    return ''


def get_language_code(problem_submit_html, language):
    """
    :desc: Retrieves language code.
    :param: `problem_submit_html` HTML text containing problem submission form.
            `language` Language Name (eg. Python3, C++, etc.)
    :return: `str` Language code.
    """

    soup = BeautifulSoup(problem_submit_html, 'html.parser')
    form = soup.find('form', id='problem-submission')
    languages_dropdown = form.find('select', id='edit-language')
    language_options = languages_dropdown.find_all('option')

    for option in language_options:
        if language.lower() + '(' in option.text.lower():
            return option['value']


@login_required
def submit_problem(problem_code, solution_file, language):
    """
    :desc: Submits the problem.
    :param: `problem_code` Code of the problem.
            `solution_file` Path of the solution file.
            `language` Language Name (eg. Python3, C++, etc.)
    :return: `resps` response information array
    """

    session = get_session()
    url = BASE_URL + '/submit/' + problem_code
    req_obj = request(session, 'GET', url)
    resps = []

    if req_obj.status_code == 200:
        form_token = get_form_token(req_obj.text)
        language_code = get_language_code(req_obj.text, language)
        if language_code is None:
            return [{'code': 400, 'data': 'Invalid language.'}]
    elif req_obj.status_code == 503:
        return [{'code': 503}]

    try:
        solution_file_obj = open(solution_file)
    except IOError:
        resps = [{
            'data_type': 'text',
            'data': 'Solution file not found. Please provide a valid path.',
            'code': 400
        }]
        return resps

    post_data = {
        'language': language_code,
        'problem_code': problem_code,
        'form_id': 'problem_submission',
        'form_token': form_token,
    }
    post_files = {'files[sourcefile]': solution_file_obj}

    req_obj = request(session, 'POST', url, data=post_data,
                      files=post_files)
    if req_obj.status_code == 200:
        print(color_text('Running code...\n', 'BLUE'))

        status_code = req_obj.url.split('/')[-1]
        url = BASE_URL + '/get_submission_status/' + status_code

        while True:
            status_req = request(session, 'GET', url)
            try:
                status_json = status_req.json()
            except ValueError:
                continue
            result_code = status_json['result_code']

            if result_code != 'wait':
                resp = {'data_type': 'text', 'code': 200}
                if result_code == 'compile':
                    error_msg = get_compilation_error(status_code)
                    compile_error_msg = u'Compilation error.\n{0}'.format(error_msg)
                    resp['data'] = color_text(compile_error_msg, 'FAIL')
                elif result_code == 'runtime':
                    error_msg = status_json['signal']
                    runtime_error_msg = u'Runtime error. {0}\n'.format(error_msg)
                    resp['data'] = color_text(runtime_error_msg, 'FAIL')
                elif result_code == 'wrong':
                    resp['data'] = color_text('Wrong answer\n', 'FAIL')
                elif result_code == 'accepted':
                    resp['data'] = 'Correct answer\n'

                resps.append(resp)

                data_rows = html_to_list(get_error_table(status_code))
                resps.append({
                    'data_type': 'table',
                    'code': 200,
                    'data': data_rows
                })

                return resps
    elif req_obj.status_code == 503:
        return [{'code': 503}]


@sort_it
def search_problems(sort, order, search_type):
    """
    :desc: Retrieves problems of the specific type.
    :param: `search_type` 'school'/ 'easy'/ 'medium'/ 'hard'/ 'challenge'/ 'extcontest'
            / contest code (eg: OCT17, nov16, etc.)
    """

    session = get_session()
    search_types = ['school', 'easy', 'medium', 'hard', 'challenge', 'extcontest']

    is_contest = False
    if search_type.lower() in search_types:
        url = BASE_URL + '/problems/' + search_type.lower()
    else:
        url = BASE_URL + '/' + search_type.upper()
        is_contest = True

    req_obj = request(session, 'GET', url)
    resp = {'code': 503}

    if req_obj.status_code == 200:
        soup = BeautifulSoup(req_obj.text, 'html.parser')
        table_html = str(soup.find_all('table')[1])
        data_rows = html_to_list(table_html)
        resp = {
            'data_type': 'table',
            'data': data_rows,
            'code': 200
        }

        if is_contest:
            contest_timer_block = soup.find_all('div', attrs={'class': 'rounded-block'})[0]
            timer_calc_script = contest_timer_block.find_all('script')

            if timer_calc_script:
                script_text = timer_calc_script[0].text
                end_date_str = re.search(r'new Date\("([a-zA-Z0-9 ,:]*)"\)', script_text).group(1)
                end_date_obj = datetime.strptime(end_date_str, '%B %d, %Y %H:%M:%S')
                now = datetime.now()
                diff = end_date_obj - now

                days = str(diff.days)
                hours = str(diff.seconds // 3600)
                minutes = str((diff.seconds % 3600) // 60)
                seconds = str((diff.seconds % 3600) % 60)

                time_left_text = color_text('Contest ends in ', 'BOLD') + days + ' days, ' +\
                    hours + ' hours, ' + minutes + ' minutes, ' + seconds + ' seconds.'
            else:
                time_left_text = color_text('Contest ended.', 'BOLD')

            resp['extra'] = time_left_text

    return resp


def get_tags(sort, order, tags):
    """
    :desc: Prints all tags or problems tagged with `tags`.
    :param: `tags` list of input tags
    :return: `resp` response information dict
    """

    if len(tags) == 0:
        return get_all_tags()
    else:
        return get_problem_tags(sort, order, tags)


def get_all_tags():
    """
    :desc: Prints all tags.
    :return: `resp` response information dict
    """

    session = get_session()
    url = BASE_URL + '/get/tags/problems'
    req_obj = request(session, 'GET', url)
    resp = {'code': 503}

    if req_obj.status_code == 200:
        all_tags = req_obj.json()
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

        resp = {'code': 200, 'data': data_rows, 'data_type': 'table'}

    return resp


@sort_it
def get_problem_tags(sort, order, tags):
    """
    :desc: Prints problems tagged with `tags`.
    :params: `tags` list of input tags
    :return: `resp` response information dict
    """

    session = get_session()
    url = BASE_URL + '/get/tags/problems/' + ','.join(tags)
    req_obj = request(session, 'GET', url)
    resp = {'code': 503}

    if req_obj.status_code == 200:
        all_tags = req_obj.json()
        data_rows = [PROBLEM_LIST_TABLE_HEADINGS]
        all_tags = all_tags['all_problems']
        resp = {'code': 200}

        if all_tags == []:
            resp['code'] = 404
            resp['extra'] = "Sorry, there are no problems with the following tags!"
        else:
            for key, value in all_tags.items():
                problem_info = []
                problem_info.append(value.get('code', ''))
                problem_info.append(value.get('name', ''))
                problem_info.append(str(value.get('attempted_by', '')))
                try:
                    accuracy = (value.get('solved_by') / value.get('attempted_by')) * 100
                    problem_info.append(str(math.floor(accuracy)))
                except TypeError:
                    problem_info.append('')
                data_rows.append(problem_info)
            resp['data'] = data_rows
            resp['data_type'] = 'table'

    return resp


@sort_it
def get_ratings(sort, order, country, institution, institution_type, page, lines):
    """
    :desc: displays the ratings of users. Result can be filtered according to
           the country, institution, institution_type and sets. `line` decide the
           number of lines to be shown. `page` tells which page of the result is to be shown
    :param: `country` filter for users
            `institution` filter for users
            `institution_type` filter for users
    """
    session = get_session()
    url = BASE_URL + '/api/ratings/all?sortBy=global_rank&order=asc'
    params = {
        'page': str((page or 1)),
        'itemsPerPage': str((lines or DEFAULT_NUM_LINES)),
        'filterBy': ''
    }

    if country:
        params['filterBy'] += 'Country=' + country + ";"
    if institution:
        institution = institution.title()
        params['filterBy'] += 'Institution=' + institution + ";"
    if institution_type:
        params['filterBy'] += 'Institution type=' + institution_type + ";"

    req_obj = request(session, 'GET', url, params=params)
    resp = {'code': 503}

    if req_obj.status_code == 200:
        ratings = req_obj.json().get('list')
        data_rows = [RATINGS_TABLE_HEADINGS]

        for user in ratings:
            temp = []
            temp.append(str(user['global_rank']) + "(" + str(user['country_rank']) + ")")
            temp.append(user['username'])
            temp.append(str(user['rating']))
            temp.append(str(user['diff']))
            data_rows.append(temp)
        if len(ratings) == 0:
            resp = {
                'code': 404,
                'data': 'Oops! we don\'t have data.',
                'data_type': 'text'
            }
        else:
            resp = {
                'code': 200,
                'data': data_rows,
                'data_type': 'table'
            }

        return resp
    return resp


def get_contests(skip_past_contests):
    """
    :desc: Retrieves contests.
    :param: `skip_past_contests` Skips printing past contests, if True
    :return: `resps` response information array
    """

    session = get_session()
    url = BASE_URL + '/contests'
    req_obj = request(session, 'GET', url)
    resps = []

    if req_obj.status_code == 200:
        soup = BeautifulSoup(req_obj.text, 'html.parser')
        tables = soup.find_all('table')
        labels = ['Present', 'Future', 'Past']
        limit = 3 if skip_past_contests else 4

        for i in range(1, limit):
            resps.append({
                'data': color_text(labels[i-1] + ' Contests:\n', 'BOLD')
            })

            data_rows = html_to_list(str(tables[i]))
            resps.append({
                'data': data_rows,
                'data_type': 'table'
            })
    elif req_obj.status_code == 503:
        resps = [{'code': 503}]

    return resps


@sort_it
def get_solutions(sort, order, problem_code, page, language, result, username):
    """
    :desc: Retrieves solutions list of a problem.
    :param: `problem_code` Code of the problem.
            `page` Page Number
    """

    session = get_session()
    params = {'page': page - 1} if page != 1 else {}
    url = BASE_URL + '/status/' + problem_code.upper()
    INVALID_PROBLEM_CODE_MSG = 'Invalid Problem Code.'

    if language:
        req_obj = request(session, 'GET', url)
        soup = BeautifulSoup(req_obj.text, 'html.parser')
        lang_dropdown = soup.find('select', id='language')
        options = lang_dropdown.find_all('option')

        for option in options:
            if language.upper() == option.text.strip().upper():
                params['language'] = option['value']
                break
    if result:
        params['status'] = RESULT_CODES[result.upper()]
    if username:
        params['handle'] = username

    req_obj = request(session, 'GET', url, params=params)

    if req_obj.status_code == 200:
        if 'SUBMISSIONS FOR ' in req_obj.text:
            soup = BeautifulSoup(req_obj.text, 'html.parser')
            solution_table = soup.find_all('table')[2]
            page_info = soup.find('div', attrs={'class': 'pageinfo'})
            resp = {
                'code': 200,
                'data_type': 'table'
            }

            rows = solution_table.find_all('tr')
            headings = rows[0].find_all('th')
            headings[-1].extract()

            for row in rows[1:]:
                cols = row.find_all('td')
                cols[-1].extract()

            data_rows = html_to_list(str(solution_table))
            resp['data'] = data_rows

            if page_info:
                resp['extra'] = '\nPage: ' + page_info.text
        else:
            resp = {
                'code': 404,
                'data': INVALID_PROBLEM_CODE_MSG,
                'data_type': 'text'
            }
    elif req_obj.status_code == 503:
        resp = {'code': 503}

    return resp


def get_solution(solution_code):
    """
    :desc: Retrieves a solution
    :param: `solution_code` Code of the solution.
    :return: `resps` response information array
    """

    session = get_session(fake_browser=True)
    url = BASE_URL + '/viewsolution/' + solution_code
    req_obj = request(session, 'GET', url)
    resps = []

    if req_obj.status_code == 200:
        if 'Solution: ' + solution_code in req_obj.text:
            soup = BeautifulSoup(req_obj.text, 'html.parser')

            ol = soup.find('ol')
            lis = ol.find_all('li')
            status_table = soup.find('table', attrs={'class': 'status-table'})

            code = ''
            for li in lis:
                code += li.text + '\n'

            headings = '\n' + color_text('Solution:', 'BOLD') + '\n' +\
                       code + '\n' + color_text('Submission Info:', 'BOLD') + '\n'
            resps.append({
                'data': headings,
                'pager': True
            })

            data_rows = html_to_list(str(status_table))
            resps.append({
                'data': data_rows,
                'data_type': 'table'
            })
        else:
            resps = [{'data': 'Invalid Solution Code.', 'code': 404}]
    elif req_obj.status_code == 403:
        resps = [{'code': 400, 'data': 'Access Denied!'}]
    elif req_obj.status_code == 503:
        resps = [{'code': 503}]

    return resps
