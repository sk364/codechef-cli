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


def sort_it(func):
    '''
    desc: decorator method to sort the specified argument
    '''
    def wrapper(*args, **kwargs):
        sort = args[0]
        orderType = args[1]
        if orderType:
            if orderType == 'asc':
                order = False
            elif orderType == 'desc':
                order = True
            else:
                resp = {
                    'code': 404,
                    'data': 'Wrong order argument entered',
                    'data_type': 'text'
                }
                return resp
        else:
            order = "asc"
        resp = func(*args, **kwargs)
        if resp['code'] == 200 and resp['data_type'] == 'table':
            data_rows = resp['data']
            if sort:
                heading = data_rows[0]
                data_rows = data_rows[1:]
                index = -1
                if sort.upper() in heading:
                    index = heading.index(sort.upper())
                    if data_rows[1][index].isdigit():
                        for data_row in data_rows:
                            if data_row[index].isdigit():
                                data_row[index] = int(data_row[index])
                            else:
                                data_row[index] = 0
                        data_rows.sort(key=lambda x: x[index], reverse=order)
                        for data_row in data_rows:
                            data_row[index] = str(data_row[index])
                    else:
                        data_rows.sort(key=lambda x: x[index], reverse=order)
                    data_rows.insert(0, heading)
                    resp['data'] = data_rows
                else:
                    resp = {
                        'code': 404,
                        'data': 'Wrong sorting argument entered',
                        'data_type': 'text'
                    }
        return resp
    return wraps(func)(wrapper)
