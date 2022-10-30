import urllib.parse
from typing import Any

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from lxml import etree
from lxml.builder import E

from api.user_utils import _user, _user_count
from modules import utils
from modules.dependencies import commons_params, database, langs
from modules.utils import LangsNegociation, i10n_select_lang

router = APIRouter()


#  TODO use i18n
def _(s):
    return s


class XMLResponse(Response):
    media_type = "text/xml; charset=utf-8"

    def render(self, content: Any) -> bytes:
        return etree.tostring(content, pretty_print=True)


class RSSResponse(XMLResponse):
    media_type = "application/rss+xml"


@router.get("/byuser")
def byUser():
    return RedirectResponse("byuser/")


@router.get("/byuser/{username}.{format}")
async def user(
    username: str,
    format: str,
    request: Request,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
    langs: LangsNegociation = Depends(langs.langs),
):
    if format in ["rss", "gpx", "kml", "josm", "csv"]:
        return RedirectResponse(
            f"{utils.website}/api/0.3/issues.{format}?{request.url.query}&username={urllib.parse.quote(username)}"
        )

    params, username, errors = await _user(params, db, username)

    return dict(
        username=username,
        users=params.users,
        website=utils.website + "/" + i10n_select_lang(langs),
        main_website=utils.main_website,
        remote_url_read=utils.remote_url_read,
    )


@router.get("/byuser_count/{username}.rss", response_class=RSSResponse)
async def user_count(
    username: str,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
):
    count = await _user_count(params, db, username)
    xml = E.rss(
        E.channel(
            E.title("Osmose - " + username),
            E.description(_("Statistics for user {0}").format(username)),
            E.link("{}/byuser/{}".format(utils.website, username)),
            E.item(
                E.title(
                    _("Number of level {level} issues: {count}").format(
                        level=1, count=count[1]
                    )
                )
            ),
            E.item(
                E.title(
                    _("Number of level {level} issues: {count}").format(
                        level=2, count=count[2]
                    )
                )
            ),
            E.item(
                E.title(
                    _("Number of level {level} issues: {count}").format(
                        level=3, count=count[3]
                    )
                )
            ),
        ),
        version="2.0",
    )
    return RSSResponse(xml)


@router.get("/byuser_count/{username}")
async def byuser_count(
    username: str,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
):
    return await _user_count(params, db, username)
