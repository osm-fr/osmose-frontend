from modules import query
from modules.params import Params


def _user(params: Params, db, lang, username: str):
    params.users = username.split(",")
    params.limit = 500
    params.full = True

    errors = query._gets(db, params)
    return [params, username, errors]


def _user_count(params: Params, db, username=None):
    if username:
        params.users = username.split(",")

    if not params.users:
        return

    res = query._count(db, params, ["class.level"], ["class.level"])
    ret = {1: 0, 2: 0, 3: 0}
    for (l, c) in res:
        ret[l] = c

    return ret
