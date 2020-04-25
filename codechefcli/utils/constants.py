from os.path import expanduser

BASE_URL = 'https://www.codechef.com'
COOKIES_FILE_PATH = expanduser('~') + '/.cookies'
SERVER_DOWN_MSG = 'Please try again later. Seems like CodeChef server is down!'
INTERNET_DOWN_MSG = 'Nothing to show. Check your internet connection.'
UNAUTHORIZED_MSG = 'You are not logged in.'
EMPTY_AUTH_DATA_MSG = 'Username/Password field cannot be left blank.'
SESSION_LIMIT_MSG = 'Session limit exceeded!'
INCORRECT_CREDS_MSG = 'Incorrect Credentials!'
LOGIN_SUCCESS_MSG = 'Successfully logged in!'
LOGOUT_SUCCESS_MSG = 'Successfully logged out!'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like\
              Gecko) Chrome/62.0.3202.62 Safari/537.36'
RESULT_CODES = {
    'AC': 15,
    'WA': 14,
    'TLE': 13,
    'RTE': 12,
    'CTE': 11
}
RATINGS_TABLE_HEADINGS = ['GLOBAL(COUNTRY)', 'USER NAME', 'RATING', 'GAIN/LOSS']
PROBLEM_LIST_TABLE_HEADINGS = ['CODE', 'NAME', 'SUBMISSION', 'ACCURACY']
DEFAULT_NUM_LINES = 20
BCOLORS = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'GREEN': '\033[92m',
    'WARNING': '\033[93m',
    'FAIL': '\033[91m',
    'ENDC': '\033[0m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m'
}
INVALID_USERNAME = '##no_login##'
IMAGE_DIR = "problem_images"
