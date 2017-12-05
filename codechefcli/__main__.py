import argparse
from getpass import getpass

from .auth import login, logout
from .problems import get_description, search_problems, submit_problem, get_contests
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
    parser.add_argument('--problem', '-p', required=False, metavar='<Problem Code>')
    parser.add_argument('--user', '-u', required=False, metavar='username')
    parser.add_argument('--submit', nargs=3, required=False,
                        metavar=('<Problem Code>', '<Solution File Path>', '<Language>'),
                        help='Language is case-insensitive. \
                              Few examples: C++, C, Python, Python3, java, etc.')
    parser.add_argument('--search', required=False, metavar='<Contest Code>',
                        help='Contest code examples - OCT17, COOK88')
    parser.add_argument('--contests', required=False, action='store_true',
                        help='Get All Contests')
    return parser


def main():
    """
    :desc: Entry point method
    """

    parser = create_parser()
    args = vars(parser.parse_args())

    username = args['login']
    is_logout = args['logout']
    problem_code = args['problem']
    search_username = args['user']
    submit = args['submit']
    contest_code = args['search']
    contests = args['contests']

    if username != '##no_login##':
        prompt('login', username=username)
        exit(0)

    elif is_logout:
        logout()
        exit(0)

    elif problem_code:
        print(get_description(problem_code))

    elif search_username:
        print(get_user(search_username))

    elif submit:
        submit_problem(*submit)

    elif contest_code:
        search_problems(contest_code)

    elif contests:
        get_contests()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
