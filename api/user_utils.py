from typing import Any, Dict, List, Optional

from asyncpg import Connection

from modules import query
from modules.dependencies.commons_params import Params


async def _user(params: Params, db: Connection, username: str) -> List[Dict[str, Any]]:
    params.users = username.split(",")
    params.limit = 500
    params.full = True

    errors = await query._gets(db, params)
    return list(map(dict, errors))


async def _user_count(
    params: Params, db: Connection, username: Optional[str] = None
) -> Dict[int, int]:
    if username:
        params.users = username.split(",")

    if not params.users:
        return

    res = await query._count(db, params, ["class.level"], ["class.level"])
    ret = {1: 0, 2: 0, 3: 0}
    for r in res:
        ret[r["level"]] = r["count"]

    return ret
