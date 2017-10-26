import requests
from http.cookiejar import LWPCookieJar

from .constants import COOKIES_FILE_PATH


def get_session():
    session = requests.Session()
    session.cookies = LWPCookieJar(filename=COOKIES_FILE_PATH)
    session.cookies.load(ignore_discard=True, ignore_expires=True)
    return session

