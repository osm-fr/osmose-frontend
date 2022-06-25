from uuid import UUID

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException

from modules import utils
from modules.dependencies import database, langs
from modules.utils import LangsNegociation

from .false_positive_utils import _get

router = APIRouter()


@router.get("/0.3/false-positive/{uuid}", tags=["issues"])
async def fp_uuid(
    uuid: UUID,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
):
    marker, columns = await _get(db, "false", uuid=uuid)
    if not marker:
        raise HTTPException(status_code=410, detail="Id is not present in database.")

    lat = str(marker["lat"])
    lon = str(marker["lon"])
    title = utils.i10n_select(marker["title"], langs)
    subtitle = utils.i10n_select(marker["subtitle"], langs)
    item = marker["item"] or 0
    date = marker["date"].isoformat() or 0

    return {
        "lat": lat,
        "lon": lon,
        "minlat": float(lat) - 0.002,
        "maxlat": float(lat) + 0.002,
        "minlon": float(lon) - 0.002,
        "maxlon": float(lon) + 0.002,
        "id": uuid,
        "title": title,
        "subtitle": subtitle,
        "b_date": None,  # Keep for retro compatibility
        "item": item,
        "date": date,
    }


@router.delete("/0.3/false-positive/{uuid}", tags=["issues"])
async def fp_delete_uuid(uuid: UUID, db: Connection = Depends(database.db)):
    m = await db.fetchrow(
        "SELECT uuid FROM markers_status WHERE status = $1 AND uuid = $2", "false", uuid
    )
    if not m:
        raise HTTPException(status_code=410)

    async with db.transaction():
        await db.execute(
            "DELETE FROM markers_status WHERE status = $1 AND uuid = $2", "false", uuid
        )

    return
