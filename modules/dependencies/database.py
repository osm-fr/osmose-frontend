import json
from typing import AsyncGenerator, Dict, List, Union

from asyncpg import Connection, Pool, connect, create_pool
from asyncpg.pool import PoolConnectionProxy

from .. import utils


class Database:
    pool: Pool

    async def create_pool(self) -> None:
        pool = await create_pool(
            dsn=utils.db_dsn,
            init=add_json_support,
        )
        if pool:
            self.pool = pool
        else:
            raise RuntimeError("Cannot create pool")


database = Database()


async def startup() -> None:
    await database.create_pool()


def _encoder(value: Union[str, List, Dict]) -> bytes:
    return b"\x01" + json.dumps(value).encode("utf-8")


def _decoder(value) -> Union[str, List, Dict]:
    return json.loads(value[1:].decode("utf-8"))


async def add_json_support(connection: Union[Connection, PoolConnectionProxy]) -> None:
    await connection.set_type_codec(
        "jsonb",
        encoder=_encoder,
        decoder=_decoder,
        schema="pg_catalog",
        format="binary",
    )

    await connection.set_type_codec(
        "json", encoder=json.dumps, decoder=json.loads, schema="pg_catalog"
    )


async def get_dbconn() -> Connection:
    connection = await connect(dsn=utils.db_dsn)
    await add_json_support(connection)
    return connection


async def db() -> AsyncGenerator[PoolConnectionProxy, None]:
    async with database.pool.acquire() as connection:
        async with connection.transaction(readonly=True):
            yield connection


async def db_rw() -> AsyncGenerator[PoolConnectionProxy, None]:
    async with database.pool.acquire() as connection:
        async with connection.transaction():
            yield connection
