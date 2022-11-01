from typing import Optional
from uuid import UUID, uuid4

from fastapi import Depends, FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import HTMLResponse, RedirectResponse

from modules import utils
from modules.dependencies import database

from . import byuser, editor, false_positive, issue, issues, map
from .tool import oauth, xmldict
from .tool.session import SessionData, backend, cookie, verifier

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


@app.get("/login")
async def login(session_id: Optional[UUID] = Depends(cookie)):
    if session_id:
        await backend.delete(session_id)

    (url, oauth_tokens) = oauth.fetch_request_token()
    session = uuid4()
    await backend.create(session, SessionData(oauth_tokens=oauth_tokens))

    response = RedirectResponse(url)
    cookie.attach_to_response(response, session)
    return response


@app.get("/logout")
async def logout(response: Response, session_id: Optional[UUID] = Depends(cookie)):
    if session_id:
        await backend.delete(session_id)
        cookie.delete_from_response(response)
    return RedirectResponse("map/")


@app.get("/oauth")
async def oauth_(
    session_id: UUID = Depends(cookie),
    session_data: Optional[SessionData] = Depends(verifier),
):
    print(session_data)
    if session_id and session_data:
        try:
            oauth_tokens = oauth.fetch_access_token(session_data.oauth_tokens)
            session_data.oauth_tokens = oauth_tokens
            user_request = oauth.get(
                oauth_tokens, utils.remote_url + "api/0.6/user/details"
            )
            if user_request:
                session_data.user = xmldict.xml_to_dict(user_request)
            await backend.update(session_id, session_data)
        except Exception:
            pass
    return RedirectResponse("map/")


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
