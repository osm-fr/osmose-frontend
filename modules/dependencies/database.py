import json

import asyncpg

from .. import utils


class Database:
    async def create_pool(self):
        self.pool = await asyncpg.create_pool(dsn=utils.db_dsn)


database = Database()


async def startup():
    await database.create_pool()


async def db():
    async with database.pool.acquire() as connection:

        def _encoder(value):
            return b"\x01" + json.dumps(value).encode("utf-8")

        def _decoder(value):
            return json.loads(value[1:].decode("utf-8"))

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

        yield connection
