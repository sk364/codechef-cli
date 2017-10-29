import argparse
import sys
from getpass import getpass

from .auth import login, logout, get_other_active_sessions
from .problems import get_description


try:
    input = raw_input
except NameError:
    pass


def prompt(action, *args, **kwargs):
    if action == 'login':
        if not kwargs.get('username', None):
            username = input('Username: ')
        else:
            username = kwargs['username']

        password = getpass()
        login(username, password)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--login', '-l', required=False, nargs='?', metavar='username', default='##no_login##')
    parser.add_argument('--logout', required=False, action='store_true')
    parser.add_argument('--problem', '-p', required=False)
    if len(sys.argv) == 1:
        parser.print_help()
        exit(0)

    return vars(parser.parse_args())


def main():
    args = parse_args()

    username = args['login']
    is_logout = args['logout']
    problem_code = args['problem']

    if username != '##no_login##':
        prompt('login', username=username)
        exit(0)

    if is_logout:
        logout()
        exit(0)

    if problem_code:
        desc = get_description(problem_code)
        if desc:
            print (desc)

if __name__ == '__main__':
    main()

