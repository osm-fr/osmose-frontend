from collections import OrderedDict

from bottle import default_app, route

from .modules.params import Params
from .user_utils import _user, _user_count

app_0_2 = default_app.pop()


@app_0_2.route("/user/<username>")
@route("/user/<username>")
def user(db, lang, username: str):
    params = Params()
    params, username, errors = _user(params, db, lang, username)

    out = OrderedDict()
    for res in errors:
        res["timestamp"] = str(res["timestamp"])
        res["lat"] = float(res["lat"])
        res["lon"] = float(res["lon"])
    out["issues"] = list(map(dict, errors))
    return out


@app_0_2.route("/user_count/<username>")
@route("/user_count/<username>")
def user_count(db, lang, username: str):
    params = Params()
    count = _user_count(db, username)
    return count


default_app.push(app_0_2)
