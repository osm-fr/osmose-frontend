import urllib.parse
from typing import Any, Dict, Union

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import RedirectResponse
from lxml import etree
from lxml.builder import E  # type: ignore

from api.user_utils import _user_count
from modules import utils
from modules.dependencies import commons_params, database, i18n, langs
from modules.utils import LangsNegociation, i10n_select_lang

router = APIRouter()


class XMLResponse(Response):
    media_type = "text/xml; charset=utf-8"

    def render(self, content: Any) -> bytes:
        return etree.tostring(content, pretty_print=True)


class RSSResponse(XMLResponse):
    media_type = "application/rss+xml"


@router.get("/byuser")
def byUser() -> RedirectResponse:
    return RedirectResponse("byuser/")


@router.get("/byuser/{username}.{format}")
async def user(
    username: str,
    format: str,
    request: Request,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
    langs: LangsNegociation = Depends(langs.langs),
) -> Union[RedirectResponse, Dict[str, Any]]:
    if format in ["rss", "gpx", "kml", "josm", "csv"]:
        return RedirectResponse(
            f"{utils.website}/api/0.3/issues.{format}?{request.url.query}&username={urllib.parse.quote(username)}"
        )

    return dict(
        username=username,
        users=username.split(","),
        website=utils.website + "/" + i10n_select_lang(langs),
        main_website=utils.main_website,
        remote_url_read=utils.remote_url_read,
    )


@router.get("/byuser_count/{username}.rss", response_class=RSSResponse)
async def user_count(
    username: str,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
    _=Depends(i18n.i18n),
) -> RSSResponse:
    count = await _user_count(params, db, username)
    counts = (
        [
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
        ]
        if count
        else []
    )

    xml = E.rss(
        E.channel(
            E.title("Osmose - " + username),
            E.description(_("Statistics for user {}").format(username)),
            E.link("{}/byuser/{}".format(utils.website, username)),
            *counts,
        ),
        version="2.0",
    )
    return RSSResponse(xml)
