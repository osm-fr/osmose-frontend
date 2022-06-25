from asyncpg import Connection
from fastapi import APIRouter, Depends, Request

from modules.dependencies import database

from .modules.params import Params
from .user_utils import _user, _user_count

router = APIRouter()


@router.get("/0.3/user/{username}", tags=["users"])
async def user(request: Request, username: str, db: Connection = Depends(database.db)):
    params = Params(request)
    params, username, errors = await _user(params, db, username)

    return {"issues": list(map(dict, errors))}


@router.get("/0.3/user_count/{username}", tags=["users"])
async def user_count(
    request: Request, username: str, db: Connection = Depends(database.db)
):
    params = Params(request)
    return await _user_count(params, db, username)
