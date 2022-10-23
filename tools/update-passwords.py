#! /usr/bin/env python3

import asyncio
import builtins
import importlib
import inspect
import sys

from modules.dependencies import database


async def main():
    db = await database.get_dbconn()

    for res in await db.fetch("SELECT COALESCE(max(id)+1, 1) FROM sources"):
        source = res[0]

    async def update_pass(
        country, analyser, password, contact="Jocelyn Jaubert <jocelyn@osm1.crans.org>"
    ):
        global source

        row = await db.fetch(
            """
SELECT
    id,
    password
FROM sources
    JOIN sources_password ON
        sources.id = source_id
WHERE
    country=$1 AND
    analyser=$2
""",
            country,
            analyser,
        )
        if len(row) >= 1:
            for r in row:
                prev_password = r["password"]
                if prev_password == password:
                    return
            # try to update password for an analyse
            await db.execute(
                """
INSERT INTO
    sources_password (source_id, password)
VALUES
    ((SELECT id FROM sources WHERE country=$1 AND analyser=$2), $3)
""",
                country,
                analyser,
                password,
            )
            print(
                f"Created password={password} where country={country} analyser={analyser}"
            )
            return

        else:
            row = await db.fetch(
                "SELECT id FROM sources WHERE country=$1 AND analyser=$2",
                country,
                analyser,
            )
            if len(row) == 1:
                cur_source = row[0]["id"]
                await db.execute(
                    "INSERT INTO sources_password (source_id, password) VALUES ($1, $2)",
                    cur_source,
                    password,
                )
                print(
                    f"Inserted password={password} where country={country} analyser={analyser}"
                )
                return

        if len(row) > 0:
            return

        if len(row) == 0:
            # otherwise, create a new entry in database
            print(
                f"Inserting country={country} analyser={analyser} source={source} password={password}"
            )
            try:
                await db.execute(
                    "INSERT INTO sources (id, country, analyser) VALUES ($1, $2, $3)",
                    source,
                    country,
                    analyser,
                )
                await db.execute(
                    "INSERT INTO sources_password (source_id, password) VALUES ($1, $2)",
                    source,
                    password,
                )
                source += 1

            except Exception:
                print(
                    f"Failure on country={country} analyser={analyser} password={password}"
                )
                raise

        else:
            print(
                f"Updated country={country} analyser={analyser} where password={password}"
            )
            return

    if len(sys.argv) > 1:
        sys.path.insert(0, sys.argv[1])
    else:
        sys.path.insert(0, "../../backend")

    # Don't load translations, as not necessary
    def translate(str, *args):
        pass

    builtins.T_ = translate
    builtins.T_f = translate

    import osmose_config

    for (country, country_config) in osmose_config.config.items():
        if country_config.analyser_options["project"] != "openstreetmap":
            continue
        for analyser, password in country_config.analyser.items():
            if password != "xxx":
                a = importlib.import_module(
                    "analysers.analyser_" + analyser, package="."
                )
                m = inspect.getmembers(a)
                for name, obj in m:
                    if (
                        inspect.isclass(obj)
                        and obj.__module__ == "analysers.analyser_" + analyser
                        and (name.startswith("Analyser") or name.startswith("analyser"))
                    ):
                        analyser_name = name[len("Analyser_") :]

                        await update_pass(country, analyser_name, password)


if __name__ == "__main__":
    asyncio.run(main())
