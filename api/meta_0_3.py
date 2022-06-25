from typing import Dict, List

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request

from modules import query_meta
from modules.dependencies import database, langs
from modules.utils import LangsNegociation

router = APIRouter()


def _map_items(categories):
    for categorie in categories:
        categorie["categ"] = categorie["id"]
        del categorie["id"]
        for item in categorie["items"]:
            item["categ"] = item["categorie_id"]
            del item["categorie_id"]
    return categories


@router.get(
    "/0.3/items",
    response_model=Dict[str, List[Dict]],
    tags=["metadata"],
)
async def items(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
):
    return {"categories": _map_items(await query_meta._items(db, langs=langs))}


@router.get(
    "/0.3/items/{item}/class/{classs}",
    response_model=Dict[str, List[Dict]],
    tags=["metadata"],
)
async def items_class(
    request: Request,
    item: int,
    classs: int,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
):
    return {
        "categories": (
            await query_meta._items(db, item=item, classs=classs, langs=langs)
        )
    }


@router.get("/0.3/countries", response_model=Dict[str, List[str]], tags=["metadata"])
async def countries(db: Connection = Depends(database.db)):
    return {"countries": await query_meta._countries(db)}


@router.get("/0.3/tags", response_model=Dict[str, List[str]], tags=["metadata"])
async def tags(db: Connection = Depends(database.db)):
    return {"tags": await query_meta._tags(db)}
