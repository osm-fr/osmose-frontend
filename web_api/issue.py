from typing import Any, Dict
from uuid import UUID

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException

from api.issue_utils import _get, _keys, t2l
from modules import utils
from modules.dependencies import database

router = APIRouter()


@router.get("/issue/{uuid}.json")
async def display(
    uuid: UUID,
    db: Connection = Depends(database.db),
) -> Dict[str, Any]:
    marker = await _get(db, uuid=uuid)
    if not marker:
        raise HTTPException(status_code=410, detail="Id is not present in database.")

    for e in marker["elems"] or []:
        e["tags"] = t2l.addLinks(e.get("tags", {}))

    for fix_group in marker["fixes"] or []:
        for f in fix_group:
            f["create"] = t2l.addLinks(f["create"])
            f["modify"] = t2l.addLinks(f["modify"])
            f["delete"] = _keys(f["delete"])

    marker = dict(marker)
    marker["timestamp"] = str(marker["timestamp"])
    return dict(
        uuid=uuid,
        marker=marker,
        main_website=utils.main_website,
    )
