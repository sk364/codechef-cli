import argparse
import sys

from codechefcli.auth import login, logout
from codechefcli.helpers import print_response
from codechefcli.problems import (RESULT_CODES, get_contest_problems,
                                  get_contests, get_description, get_ratings,
                                  get_solution, get_solutions, get_tags,
                                  search_problems, submit_problem)
from codechefcli.teams import get_team
from codechefcli.users import get_user

GENERIC_RESP = {"code": 500, "data": "Unexpected stuff is happening here"}
CC_PRACTICE = "PRACTICE"
SEARCH_TYPES = ['school', 'easy', 'medium', 'hard', 'challenge', 'extcontest']
INSTITUTION_TYPES = ['School', 'Organization', 'College']
INVALID_USERNAME = '##no_login##'
DEFAULT_PAGE = 1
DEFAULT_NUM_LINES = 20


def create_parser():
    parser = argparse.ArgumentParser()

    # auth
    parser.add_argument('--login', '-l', required=False, nargs='?', metavar='username',
                        default=INVALID_USERNAME)
    parser.add_argument('--logout', required=False, action='store_true')
    parser.add_argument('--disconnect-sessions', required=False, action='store_true',
                        default=False, help='Disconnects active sessions, \
                                             when session limit exceeded.')

    # user & team info
    parser.add_argument('--user', '-u', required=False, metavar='<Username>',
                        help='Get user information. This arg can also be used for filtering data.')
    parser.add_argument('--team', required=False, metavar='<Name>',
                        help='Get team information.')

    # ratings & its filters
    parser.add_argument('--ratings', required=False, action="store_true", help='Displays user \
                        ratings. Filters: `--country`, `--institution`, `--institution-type`')
    parser.add_argument('--country', required=False, metavar='<Country>',
                        help='Country filter. Eg: India, "United States", etc.')
    parser.add_argument('--institution', required=False, metavar='<Institution>',
                        help='Institution Filter')
    parser.add_argument('--institution-type', required=False, metavar='<Type>',
                        choices=INSTITUTION_TYPES, help='Institution Type Filter')

    # problems: get, submit & search
    parser.add_argument('--problem', required=False, metavar='<Code>',
                        help='Get Problem Description.')
    parser.add_argument('--submit', nargs=3, required=False,
                        metavar=('<Problem Code>', '<Solution File Path>', '<Language>'),
                        help='Eg: C++, C, Python, Python3, java, etc. (case-insensitive)')
    parser.add_argument('--search', required=False, metavar='<Type>', choices=SEARCH_TYPES,
                        help='Search practice problems filter (case-insensitive)')

    # contests and its filters
    parser.add_argument('--contests', required=False, action='store_true',
                        help='Get All Contests')
    parser.add_argument('--contest', required=False, metavar='<Code>',
                        help='Get Contest Problems')
    parser.add_argument('--show-past', required=False, action='store_true',
                        help='Shows only past contests.')

    # solutions & its filters
    parser.add_argument('--solutions', required=False, metavar='<Problem Code>',
                        help='Get problem\'s solutions list')
    parser.add_argument('--solution', required=False, metavar='<Code>',
                        help='Get specific solution')
    parser.add_argument('--language', required=False,
                        help='Language filter. Eg: C++, C, python3, java. (case-insensitive)')
    parser.add_argument('--result', '-r', required=False, choices=RESULT_CODES.keys(),
                        help='Result type filter (case-insensitive)')

    # tags
    parser.add_argument('--tags', required=False, nargs='*', metavar="<Tag Name>",
                        help='No args: get all tags. Add args to get problems in the tag')

    # common
    parser.add_argument('--lines', required=False, metavar='<Lines>', default=DEFAULT_NUM_LINES,
                        type=int, help=f'Limit number of lines. Default: {DEFAULT_NUM_LINES}')
    parser.add_argument('--sort', required=False, metavar='<Sort>',
                        help='utility argument to sort the results')
    parser.add_argument('--order', required=False, metavar='<Order>', default='asc',
                        help='utility argument to specify the sorting order; default: `asc` \
                        `asc` for ascending; `desc` for descending')
    parser.add_argument('--page', '-p', required=False, metavar='<Number>', default=DEFAULT_PAGE,
                        type=int, help=f'Gets specific page. Default: {DEFAULT_PAGE}')

    return parser


def main(argv=None):
    if argv is None:
        argv = sys.argv

    try:
        parser = create_parser()
        args = parser.parse_args(argv[1:])

        username = args.login
        is_logout = args.logout
        disconnect_sessions = args.disconnect_sessions

        user = args.user
        team = args.team

        ratings = args.ratings
        country = args.country
        institution = args.institution
        institution_type = args.institution_type

        problem_code = args.problem
        submit = args.submit
        search = args.search

        contest = args.contest
        contests = args.contests
        show_past = args.show_past

        tags = args.tags

        solutions = args.solutions
        solution_code = args.solution
        language = args.language
        result = args.result

        lines = args.lines
        sort = args.sort
        order = args.order
        page = args.page

        resps = []

        if username != INVALID_USERNAME:
            resps = login(username=username, disconnect_sessions=disconnect_sessions)

        elif is_logout:
            resps = logout()

        elif problem_code:
            resps = get_description(problem_code, contest or CC_PRACTICE)

        elif submit:
            resps = submit_problem(*submit)

        elif search:
            resps = search_problems(sort, order, search)

        elif contest:
            resps = get_contest_problems(sort, order, contest)

        elif contests:
            resps = get_contests(show_past)

        elif isinstance(tags, list):
            resps = get_tags(sort, order, tags)

        elif solutions:
            resps = get_solutions(sort, order, solutions, page, language, result, user)

        elif solution_code:
            resps = get_solution(solution_code)

        elif user:
            resps = get_user(user)

        elif team:
            resps = get_team(team)

        elif ratings:
            resps = get_ratings(sort, order, country, institution, institution_type, page, lines)

        else:
            parser.print_help()

        if resps:
            for resp in resps:
                print_response(**resp)
        else:
            print_response(**GENERIC_RESP)
    except KeyboardInterrupt:
        print('\nBye.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
