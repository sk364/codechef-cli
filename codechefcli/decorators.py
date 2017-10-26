import os

from functools import wraps
from http.cookiejar import LWPCookieJar

from .utils.constants import COOKIES_FILE_PATH


def login_required(func):
    """
    :desc: decorator method to check user's login status
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        is_login = False
        if os.path.exists(COOKIES_FILE_PATH):
            cookiejar = LWPCookieJar(filename=COOKIES_FILE_PATH)
            cookiejar.load()

            if len(cookiejar):
                is_login = True
            else:
                os.remove(COOKIES_FILE_PATH)

        if not is_login:
            print ('You are not logged in.')
            return 
        else:
            return func(*args, **kwargs)

    return wrapper

