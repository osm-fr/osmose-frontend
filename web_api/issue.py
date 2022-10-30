from uuid import UUID

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException

from api.issue_utils import _expand_tags, _get, t2l
from modules import utils
from modules.dependencies import database

router = APIRouter()


@router.get("/issue/{uuid}.json")
async def display(
    uuid: UUID,
    db: Connection = Depends(database.db),
):
    marker = await _get(db, uuid=uuid)
    if not marker:
        raise HTTPException(status_code=410, detail="Id is not present in database.")

    for e in marker["elems"] or []:
        e["tags"] = _expand_tags(e.get("tags", {}), t2l.checkTags(e.get("tags", {})))

    for fix_group in marker["fixes"] or []:
        for f in fix_group:
            f["create"] = _expand_tags(f["create"], t2l.checkTags(f["create"]))
            f["modify"] = _expand_tags(f["modify"], t2l.checkTags(f["modify"]))
            f["delete"] = _expand_tags(f["delete"], {}, True)

    marker = dict(marker)
    marker["timestamp"] = str(marker["timestamp"])
    return dict(
        uuid=uuid,
        marker=marker,
        main_website=utils.main_website,
    )
