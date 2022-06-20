from modules import query
from modules.params import Params


def _user(db, lang, username):
    params = Params()
    if username:
        params.users = username.split(",")
    params.limit = 500
    params.full = True
    username = ",".join(params.users)

    errors = query._gets(db, params)
    return [params, username, errors]


def _user_count(db, username=None):
    params = Params()
    if username:
        params.users = username.split(",")

    if not params.users:
        return

    res = query._count(db, params, ["class.level"], ["class.level"])
    ret = {1: 0, 2: 0, 3: 0}
    for (l, c) in res:
        ret[l] = c

    return ret
