from typing import Dict, Optional, Set

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse

from api.user_utils import _user_count
from modules import query_meta, utils
from modules.dependencies import commons_params, database, langs
from modules.utils import LangsNegociation

from .tool.session import SessionData, cookie, verifier

router = APIRouter()


@router.get("/map")
def errors(
    request: Request,
):
    return RedirectResponse("map/?" + request.url.query)


@router.get("/map/.json", dependencies=[Depends(cookie)])
async def index(
    request: Request,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
    langs: LangsNegociation = Depends(langs.langs),
    session_data: Optional[SessionData] = Depends(verifier),
):
    if request.url.query:
        return RedirectResponse("./#" + request.url.query)

    tags = await query_meta._tags(db)
    countries = await query_meta._countries(db)

    categories = await query_meta._items(db, langs=langs)

    item_levels: Dict[str, Set[str]] = {"1": set(), "2": set(), "3": set()}
    for categ in categories:
        for item in categ["items"]:
            del item["number"]
            for index, classs in enumerate(item["class"]):
                item["class"][index] = {
                    "class": classs["class"],
                    "title": classs["title"],
                }
            for level in item["levels"]:
                item_levels[str(level["level"])].add(item["item"])

    item_levels["1,2"] = item_levels["1"] | item_levels["2"]
    item_levels["1,2,3"] = item_levels["1,2"] | item_levels["3"]

    sql = """
SELECT
    timestamp
FROM
    updates_last
ORDER BY
    timestamp
LIMIT
    1
OFFSET
    (SELECT COUNT(*)/2 FROM updates_last)
"""
    timestamp = await db.fetchval(sql)

    if session_data and session_data.user:
        user = session_data.user["osm"]["user"]["@display_name"]
        user_error_count = await _user_count(params, db, user)
    else:
        user = None
        user_error_count = None

    return dict(
        categories=categories,
        tags=tags,
        countries=countries,
        item_levels=item_levels,
        main_project=utils.main_project,
        timestamp=timestamp,
        languages_name=utils.languages_name,
        website=utils.website,
        remote_url_read=utils.remote_url_read,
        user=user,
        user_error_count=user_error_count,
        main_website=utils.main_website,
    )
