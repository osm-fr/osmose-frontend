#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from modules import query_meta
from modules.dependencies import database


async def main():
    db = await database.get_dbconn()
    sources = [int(x) for x in (await query_meta._sources(db)).keys()]

    tables = ["markers_counts", "markers", "markers_status", "updates"]
    for t in tables:
        for res in await db.fetch(f"SELECT source_id FROM {t} GROUP BY source_id"):
            if res["source_id"] not in sources:
                print(f"DELETE FROM {t} WHERE source_id = {res['source_id']};")


if __name__ == "__main__":
    asyncio.run(main())
