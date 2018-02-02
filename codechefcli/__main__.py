import argparse
import sys
from getpass import getpass

from .auth import login, logout
from .problems import (get_contests, get_description, get_ratings,
                       get_solution, get_solutions, get_tags, search_problems,
                       submit_problem)
from .users import get_user

# Supporting input in Python 2/3
try:
    input = raw_input
except NameError:
    pass


def prompt(action, *args, **kwargs):
    """
    :desc: Prompts the user corresponding to an action.
    :param: `action` Action name
    :return: None
    """

    if action == 'login':
        if not kwargs.get('username', None):
            username = input('Username: ')
        else:
            username = kwargs['username']

        password = getpass()
        login(username, password)


def create_parser():
    """
    :desc: Parses arguments from command line
    :return: (parser object, arguments dict)
    """

    parser = argparse.ArgumentParser()
    parser.add_argument('--login', '-l', required=False, nargs='?', metavar='username',
                        default='##no_login##')
    parser.add_argument('--logout', required=False, action='store_true')
    parser.add_argument('--problem', required=False, metavar='<Problem Code>',
                        help='Get Problem Description.')
    parser.add_argument('--user', '-u', required=False, metavar='username',
                        help='Get user information. This arg can also be used for filtering data.')
    parser.add_argument('--submit', nargs=3, required=False, metavar=('<Problem Code>',
                        '<Solution File Path>', '<Language>'), help='Eg: C++, C, Python, Python3, \
                        java, etc. (case-insensitive)')
    parser.add_argument('--search', required=False, metavar='<type>',
                        help='type is either school / easy / medium / hard / challenge / extcontest \
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
                        AC, WA, TLE, RTE, CTE. Default="ALL". (case-insensitive)')
    parser.add_argument('--tags', required=False, nargs='*', metavar="<tags>",
                        help='Prints existing tags, if no argument passed. Pass tags as arguments \
                              to search problems in a particular tag. Eg: --tags <tag 1> <tag 2> \
                               ... <tag N>')
    parser.add_argument('--ratings', required=False, action="store_true", help='displays user \
                        ratings. Can be filtered with tags like --country, --institution, \
                        --institution_type, --set. Number of lines(<40) is decided with \
                        --lines(default = 20)')
    parser.add_argument('--country', required=False, metavar='<country>',
                        help='provides country filter')
    parser.add_argument('--institution', required=False, metavar='<institution>',
                        help='provides institution filter')
    parser.add_argument('--institution_type', required=False, metavar='<institution_type>',
                        choices=['School', 'Organization', 'College'],
                        help='provides institution_type filter')
    parser.add_argument('--lines', required=False, metavar='<Lines>',
                        default=20, type=int, help='displays specified number \
                        of lines, Default: 20')
    parser.add_argument('--sort', required=False, metavar='<sortBy>',
                    help='utility argument to sort results of other arguments')

    return parser


def main():
    """
    :desc: Entry point method
    """

    try:
        parser = create_parser()
        args = vars(parser.parse_args())

        username = args['login']
        is_logout = args['logout']
        problem_code = args['problem']
        user = args['user']
        submit = args['submit']
        search = args['search']
        contests = args['contests']
        tags = args['tags']
        page = args['page']
        solution_list_problem_code = args['solutions']
        solution_code = args['solution']
        language = args['language']
        result = args['result']
        ratings = args['ratings']
        country = args['country']
        institution = args['institution']
        institution_type = args['institution_type']
        lines = args['lines']
        sort = args['sort']


        if username != '##no_login##':
            prompt('login', username=username)
            exit(0)

        elif is_logout:
            logout()
            exit(0)

        elif problem_code:
            get_description(problem_code, contest_code=search)

        elif submit:
            submit_problem(*submit)

        elif search:
            search_problems(search, sort)

        elif contests:
            get_contests()

        elif tags or tags == []:
                get_tags(tags, sort)

        elif solution_list_problem_code:
            get_solutions(solution_list_problem_code, page, language, result, user, sort)

        elif solution_code:
            get_solution(solution_code)

        elif user:
            get_user(user)

        elif ratings:
            get_ratings(country, institution, institution_type, page, lines, sort)

        else:
            parser.print_help()
    except KeyboardInterrupt:
        print('\nBye.')
    sys.exit(0)


if __name__ == '__main__':
    main()
