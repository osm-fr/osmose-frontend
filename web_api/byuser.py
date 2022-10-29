import asyncio
import urllib.parse

from bottle import redirect, request, response, route
from lxml import etree
from lxml.builder import E

from api.user_utils import _user, _user_count
from modules.dependencies.commons_params import params as async_params
from modules.dependencies.database import get_dbconn
from modules_legacy import utils


@route("/byuser")
def byUser():
    redirect("byuser/")


@route("/byuser/<username>.<format:ext>")
def user(db, lang, username, format):
    if format in ["rss", "gpx", "kml", "josm", "csv"]:
        response.status = 301
        response.set_header(
            "Location",
            f"{utils.website}/api/0.3/issues.{format}?{request.query_string}&username={urllib.parse.quote(username)}",
        )
        return

    async def t(username):
        return await _user(await async_params(), await get_dbconn(), username)

    params, username, errors = asyncio.run(t(username))

    return dict(
        username=username,
        users=params.users,
        website=utils.website + "/" + lang[0],
        main_website=utils.main_website,
        remote_url_read=utils.remote_url_read,
    )


@route("/byuser_count/<username>.rss")
def user_count(db, lang, username=None):
    async def t(username):
        return await _user_count(await async_params(), await get_dbconn(), username)

    count = asyncio.run(t(username))
    response.content_type = "application/rss+xml"
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
    return etree.tostring(xml, pretty_print=True)


@route("/byuser_count/<username>")
def byuser_count(db, lang, username=None):
    async def t(username):
        return await _user_count(await async_params(), await get_dbconn(), username)

    return asyncio.run(t(username))
