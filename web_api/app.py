import os

import beaker.middleware
import bottle
from bottle import HTTPError, error, hook, redirect, request, route, view

from modules_legacy import bottle_cors, bottle_gettext, bottle_pgsql, bottle_user, utils
from modules_legacy.osmose_bottle import ext_filter, uuid_filter

from .tool import oauth, xmldict

bottle.BaseRequest.MEMFILE_MAX = 100 * 1024 * 1024
bottle_app = bottle.default_app()
bottle_app.plugins = list(
    filter(
        lambda x: isinstance(x, bottle.JSONPlugin)
        or isinstance(x, bottle.TemplatePlugin),
        bottle_app.plugins,
    )
)


@hook("before_request")
def setup_request():
    if request:
        request.session = request.environ["beaker.session"]


session_opts = {
    "session.type": "file",
    "session.data_dir": "./web_api/session/",
    "session.cookie_expires": False,
}
app_middleware = beaker.middleware.SessionMiddleware(bottle.default_app(), session_opts)


app = bottle.default_app()

from bottle import SimpleTemplate

SimpleTemplate.defaults["get_url"] = app.get_url


app.install(bottle_pgsql.Plugin(utils.db_string))
app.install(
    bottle_cors.Plugin(
        allow_origin="*", preflight_methods=["GET", "POST", "PUT", "DELETE"]
    )
)
app.install(
    bottle_gettext.Plugin(
        "osmose-frontend", os.path.join("web", "po", "mo"), utils.allowed_languages
    )
)
app.install(bottle_user.Plugin())

app.router.add_filter("uuid", uuid_filter)
app.router.add_filter("ext", ext_filter)


@route("/login")
def login(lang):
    if "user" in request.session:
        del request.session["user"]  # logout
    (url, oauth_tokens) = oauth.fetch_request_token()
    request.session["oauth_tokens"] = oauth_tokens
    request.session.save()
    redirect(url)


@route("/logout")
def login(lang):
    if "user" in request.session:
        del request.session["user"]
        request.session.save()
    redirect("map/")


@route("/oauth")
def oauth_(lang):
    try:
        oauth_tokens = request.session["oauth_tokens"]
        oauth_tokens = oauth.fetch_access_token(
            request.session["oauth_tokens"], request
        )
        request.session["oauth_tokens"] = oauth_tokens
        try:
            user_request = oauth.get(
                oauth_tokens, utils.remote_url + "api/0.6/user/details"
            )
            if user_request:
                request.session["user"] = xmldict.xml_to_dict(user_request)
        except Exception as e:
            pass
        if "user" not in request.session:
            request.session["user"] = None
    except:
        pass
    finally:
        request.session.save()
    redirect("map/")


@bottle.route("/<:re:.*>", method="OPTIONS")
def enable_cors_generic_route():
    pass


from . import byuser, control, editor, false_positive, issue, issues, map


@route("/")
@route("/contact")
@route("/copyright")
@route("/translation")
@route("/map/")
@route("/issue/<uuid:uuid>")
@route("/false-positive/<uuid:uuid>")
@route("/issues/open")
@route("/issues/done")
@route("/issues/false-positive")
@route("/issues/matrix")
@route("/byuser/")
@route("/byuser/<username>")
@route("/control/update/<source:int>")
@route("/control/update_matrix")
@route("/control/update_summary")
@route("/control/update_summary_by_analyser")
def vue(db, uuid=None, username=None, source=None):
    return bottle.static_file("assets/index.html", root="web/public")


@bottle.route("/<filename:path>")
def static(filename):
    return HTTPError(404)


if __name__ == "__main__":
    bottle.run(
        app=app_middleware, host="0.0.0.0", port=20009, reloader=True, debug=True
    )
