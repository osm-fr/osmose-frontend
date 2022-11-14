from typing import Any, Dict
from uuid import UUID

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException

from api.false_positive_utils import _get
from modules.dependencies import database

router = APIRouter()


@router.get("/false-positive/{uuid}.json")
async def fp_(
    uuid: UUID,
    db: Connection = Depends(database.db),
) -> Dict[str, Any]:
    marker, columns = await _get(db, "false", uuid=uuid)
    if not marker:
        raise HTTPException(status_code=410, detail="Id is not present in database.")

    marker = dict(marker)
    marker["timestamp"] = str(marker["timestamp"])
    return dict(
        uuid=uuid,
        marker=marker,
    )
