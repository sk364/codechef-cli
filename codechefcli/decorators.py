import os
from functools import wraps

from .utils.constants import COOKIES_FILE_PATH

try:
    from http.cookiejar import LWPCookieJar
except ImportError:
    from cookielib import LWPCookieJar


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
            return [{'code': 401}]
        else:
            return func(*args, **kwargs)

    return wrapper
