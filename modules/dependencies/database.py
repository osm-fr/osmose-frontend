import json

import asyncpg

from .. import utils


class Database:
    async def create_pool(self):
        self.pool = await asyncpg.create_pool(dsn=utils.db_dsn)


database = Database()


async def startup():
    await database.create_pool()


def _encoder(value):
    return b"\x01" + json.dumps(value).encode("utf-8")


def _decoder(value):
    return json.loads(value[1:].decode("utf-8"))


async def add_json_support(connection):
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


async def get_dbconn():
    connection = await asyncpg.connect(dsn=utils.db_dsn)
    await add_json_support(connection)
    return connection


async def db():
    async with database.pool.acquire() as connection:
        await add_json_support(connection)
        tr = connection.transaction()
        await tr.start()
        try:
            yield connection
        finally:
            if connection.is_in_transaction():
                await tr.rollback()


async def db_rw():
    async with database.pool.acquire() as connection:
        await add_json_support(connection)
        tr = connection.transaction()
        await tr.start()
        try:
            yield connection
        except Exception:
            if connection.is_in_transaction():
                await tr.rollback()
            raise
        else:
            if connection.is_in_transaction():
                await tr.commit()
