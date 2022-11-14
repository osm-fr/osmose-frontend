from typing import Any, Dict, List, Literal, Optional

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request

from modules.dependencies import commons_params, database

from .user_utils import _user, _user_count

router = APIRouter()


@router.get("/0.3/user/{username}", tags=["users"])
async def user(
    request: Request,
    username: str,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
) -> Dict[Literal["issues"], List[Dict[str, Any]]]:
    errors = await _user(params, db, username)
    return {"issues": errors}


@router.get("/0.3/user_count/{username}", tags=["users"])
async def user_count(
    request: Request,
    username: str,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
) -> Optional[Dict[int, int]]:
    return await _user_count(params, db, username)
