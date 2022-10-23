#! /usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

from modules_legacy import utils


async def main():
    sources = [int(x) for x in utils.get_sources().keys()]
    dbconn = utils.get_dbconn()
    dbcurs = dbconn.cursor()

    tables = ["markers_counts", "markers", "markers_status", "updates"]
    for t in tables:
        dbcurs.execute(f"SELECT source_id FROM {t} GROUP BY source_id")
        for res in dbcurs.fetchall():
            if res[0] not in sources:
                print(f"DELETE FROM {t} WHERE source_id = {res[0]};")


if __name__ == "__main__":
    asyncio.run(main())
