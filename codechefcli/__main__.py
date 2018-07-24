import argparse
import sys
from getpass import getpass

from .auth import login, logout
from .problems import (get_contests, get_description, get_ratings,
                       get_solution, get_solutions, get_tags, search_problems,
                       submit_problem)
from .users import get_user
from .utils.constants import INVALID_USERNAME
from .utils.helpers import print_response

# Supporting input in Python 2/3
try:
    input = raw_input
except NameError:
    pass


def prompt(action, *args, **kwargs):
    """
    :desc: Prompts the user corresponding to an action.
    :param: `action` Action name
    """

    if action == 'login':
        if not kwargs.get('username', None):
            username = input('Username: ')
        else:
            username = kwargs['username']

        password = getpass()
        disconnect_sessions = kwargs.get('disconnect_sessions', False)

        return login(username, password, disconnect_sessions)


def create_parser():
    """
    :desc: Parses arguments from command line
    :return: (parser object, arguments dict)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--login', '-l', required=False, nargs='?', metavar='username',
                        default=INVALID_USERNAME)
    parser.add_argument('--logout', required=False, action='store_true')
    parser.add_argument('--disconnect-sessions', required=False, action='store_true',
                        default=False, help='Disconnects active sessions, \
                                             when session limit exceeded.')
    parser.add_argument('--problem', required=False, metavar='<Problem Code>',
                        help='Get Problem Description.')
    parser.add_argument('--user', '-u', required=False, metavar='<Username>',
                        help='Get user information. This arg can also be used for filtering data.')
    parser.add_argument('--submit', nargs=3, required=False, metavar=('<Problem Code>',
                        '<Solution File Path>', '<Language>'), help='Eg: C++, C, Python, Python3, \
                        java, etc. (case-insensitive)')
    parser.add_argument('--search', required=False, metavar='<Type>',
                        help='Type is either school / easy / medium / hard / challenge / extcontest \
                             / <contest code>. <contest code> examples - OCT17, COOK88.\
                             (case-insensitive)')
    parser.add_argument('--contests', required=False, action='store_true',
                        help='Get All Contests')
    parser.add_argument('--page', '-p', required=False, metavar='<Page Number>',
                        default=1, type=int, help='Gets specific page. Default: 1')
    parser.add_argument('--solutions', required=False, metavar='<Problem Code>',
                        help='Prints solutions list for a problem')
    parser.add_argument('--solution', required=False, metavar='<Solution Code>',
                        help='Prints a solution')
    parser.add_argument('--language', required=False, help='Eg: C++, C, python3, java. This arg \
                        can also be used for filtering data. (case-insensitive)')
    parser.add_argument('--result', '-r', required=False, help='Result of the solution. Choices: \
                        AC, WA, TLE, RTE, CTE. Default: "ALL". (case-insensitive)')
    parser.add_argument('--tags', required=False, nargs='*', metavar="<Tag Name>",
                        help='Prints existing tags, if no argument passed. Pass 1 or more tags as arguments \
                        to search problems in a particular tag.')
    parser.add_argument('--ratings', required=False, action="store_true", help='Displays user \
                        ratings. Available filters: --country, --institution, --institution-type. \
                        Limit output lines (<= 40) using --lines.')
    parser.add_argument('--country', required=False, metavar='<Country>',
                        help='Country filter. Eg: India, "United States", etc.')
    parser.add_argument('--institution', required=False, metavar='<Institution>',
                        help='Institution Filter. Eg: "Indian Institute of Information Technology, Design \
                        and Manufacturing, Jabalpur"')
    parser.add_argument('--institution-type', required=False, metavar='<Institution Type>',
                        choices=['School', 'Organization', 'College'],
                        help='Institution Type Filter')
    parser.add_argument('--lines', required=False, metavar='<Lines>',
                        default=20, type=int, help='Limit number of lines in output. Default: 20')
    parser.add_argument('--skip-past-contests', required=False, action='store_true',
                        help='Skips printing past contests.')
    parser.add_argument('--sort', required=False, metavar='<sortBy>',
                        help='utility argument to sort results of other arguments')
    parser.add_argument('--order', required=False, metavar='<order>', default='asc',
                        help='utility argument to specify the sorting order; default: ascending \
                        `asc` for ascending; `desc` for descending')
    return parser


def main(argv=None):
    """
    :desc: Entry point method
    """

    if argv is None:
        argv = sys.argv

    try:
        parser = create_parser()
        args = parser.parse_args(argv[1:])

        username = args.login
        is_logout = args.logout
        disconnect_sessions = args.disconnect_sessions
        problem_code = args.problem
        user = args.user
        submit = args.submit
        search = args.search
        contests = args.contests
        tags = args.tags
        page = args.page
        solution_list_problem_code = args.solutions
        solution_code = args.solution
        language = args.language
        result = args.result
        ratings = args.ratings
        country = args.country
        institution = args.institution
        institution_type = args.institution_type
        lines = args.lines
        skip_past_contests = args.skip_past_contests
        sort = args.sort
        order = args.order
        resps = []

        if username != INVALID_USERNAME:
            resps = prompt('login', username=username, disconnect_sessions=disconnect_sessions)

        elif is_logout:
            resps = logout()

        elif problem_code:
            resps = get_description(problem_code, contest_code=search)

        elif submit:
            resps = submit_problem(*submit)

        elif search:
            resps = [search_problems(sort, order, search)]

        elif contests:
            resps = get_contests(skip_past_contests)

        elif tags or tags == []:
            resps = [get_tags(sort, order, tags)]

        elif solution_list_problem_code:
            resps = [get_solutions(sort, order, solution_list_problem_code,
                     page, language, result, user)]

        elif solution_code:
            resps = get_solution(solution_code)

        elif user:
            resps = get_user(user)

        elif ratings:
            resps = [get_ratings(sort, order, country, institution, institution_type, page, lines)]

        else:
            parser.print_help()

        for resp in resps:
            print_response(**resp)
    except KeyboardInterrupt:
        print('\nBye.')
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
