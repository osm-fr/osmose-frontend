from typing import Optional
from uuid import UUID

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse

from modules.dependencies import database

from . import byuser, editor, false_positive, issue, issues, map

# from modules import utils
# from .tool import oauth, xmldict

openapi_tags = [
    {
        "name": "Private API",
        "description": "Private API. For external use refer to public API.",
    },
]

app = FastAPI(openapi_tags=openapi_tags)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Osmose-QA API",
        version="0.3",
        routes=app.routes,
    )
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


################
# @hook("before_request")
# def setup_request():
#     if request:
#         request.session = request.environ["beaker.session"]


# session_opts = {
#     "session.type": "file",
#     "session.data_dir": "./web_api/session/",
#     "session.cookie_expires": False,
# }
# app_middleware = beaker.middleware.SessionMiddleware(bottle.default_app(), session_opts)

# app.install(
#     bottle_gettext.Plugin(
#         "osmose-frontend", os.path.join("web", "po", "mo"), utils.allowed_languages
#     )
# )
# app.install(bottle_user.Plugin())
#####################


@app.get("/login")
def login(lang):
    if "user" in request.session:
        del request.session["user"]  # logout
    (url, oauth_tokens) = oauth.fetch_request_token()
    request.session["oauth_tokens"] = oauth_tokens
    request.session.save()
    redirect(url)


@app.get("/logout")
def logout(lang):
    if "user" in request.session:
        del request.session["user"]
        request.session.save()
    redirect("map/")


@app.get("/oauth")
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
        except Exception:
            pass
        if "user" not in request.session:
            request.session["user"] = None
    except Exception:
        pass
    finally:
        request.session.save()
    redirect("map/")


# CORS middleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST", "PUT", "DELETE"],
)


@app.on_event("startup")
async def startup():
    await database.startup()


# Add routes

app.include_router(byuser.router)
app.include_router(editor.router)
app.include_router(false_positive.router)
app.include_router(issue.router)
app.include_router(issues.router)
app.include_router(map.router)


@app.get("/", tags=["vue"])
@app.get("/contact", tags=["vue"])
@app.get("/copyright", tags=["vue"])
@app.get("/translation", tags=["vue"])
@app.get("/map/", tags=["vue"])
@app.get("/issue/{uuid}", tags=["vue"])
@app.get("/false-positive/{uuid}", tags=["vue"])
@app.get("/issues/open", tags=["vue"])
@app.get("/issues/done", tags=["vue"])
@app.get("/issues/false-positive", tags=["vue"])
@app.get("/issues/matrix", tags=["vue"])
@app.get("/byuser/", tags=["vue"])
@app.get("/byuser/{username}", tags=["vue"])
@app.get("/control/update/{source}", tags=["vue"])
@app.get("/control/update_matrix", tags=["vue"])
@app.get("/control/update_summary", tags=["vue"])
@app.get("/control/update_summary_by_analyser", tags=["vue"])
def vue(
    uuid: Optional[UUID] = None,
    username: Optional[str] = None,
    source: Optional[int] = None,
):
    return HTMLResponse(content=open("web/public/assets/index.html").read())
