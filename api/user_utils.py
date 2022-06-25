from typing import Union

from asyncpg import Connection

from modules import query
from modules.params import Params


async def _user(params: Params, db: Connection, username: str):
    params.users = username.split(",")
    params.limit = 500
    params.full = True

    errors = list(await query._gets(db, params))
    return [params, username, errors]


async def _user_count(
    params: Params, db: Connection, username: Union[str, None] = None
):
    if username:
        params.users = username.split(",")

    if not params.users:
        return

    res = await query._count(db, params, ["class.level"], ["class.level"])
    ret = {1: 0, 2: 0, 3: 0}
    for (l, c) in res:
        ret[l] = c

    return ret
