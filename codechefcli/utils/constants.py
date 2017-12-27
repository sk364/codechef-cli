from os.path import expanduser

BASE_URL = 'https://www.codechef.com'
COOKIES_FILE_PATH = expanduser('~') + '/.cookies'
SERVER_DOWN_MSG = 'Please try again later. Seems like CodeChef server is down!'
INTERNET_DOWN_MSG = 'Nothing to show. Check your internet connection.'
USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like\
              Gecko) Chrome/62.0.3202.62 Safari/537.36'
RESULT_CODES = {
    'AC': 15,
    'WA': 14,
    'TLE': 13,
    'RTE': 12,
    'CTE': 11
}
