#! /usr/bin/env python3

try:
    import builtins
except ImportError:
    import __builtin__ as builtins

import importlib
import inspect
import sys

import psycopg2

import modules_legacy.utils

if __name__ == "__main__":

    dbconn = modules_legacy.utils.get_dbconn()
    dbcurs = dbconn.cursor()

    dbcurs.execute("SELECT COALESCE(max(id)+1, 1) FROM sources;")
    for res in dbcurs.fetchall():
        source = res[0]

    def update_pass(
        country, analyser, password, contact="Jocelyn Jaubert <jocelyn@osm1.crans.org>"
    ):
        global source

        dbcurs.execute(
            """
SELECT
    id,
    password
FROM sources
    JOIN sources_password ON
        sources.id = source_id
WHERE
    country=%s AND
    analyser=%s
""",
            (country, analyser),
        )
        if dbcurs.rowcount >= 1:
            for r in dbcurs:
                prev_password = r["password"]
                if prev_password == password:
                    return
            # try to update password for an analyse
            dbcurs.execute(
                """
INSERT INTO
    sources_password (source_id, password)
VALUES
    ((SELECT id FROM sources WHERE country=%s AND analyser=%s), %s)
""",
                (country, analyser, password),
            )
            if dbcurs.rowcount == 1:
                print(
                    "created password=%s where country=%s analyser=%s"
                    % (password, country, analyser)
                )
                return

        elif dbcurs.rowcount == 0:
            dbcurs.execute(
                "SELECT id FROM sources WHERE country=%s AND analyser=%s;",
                (country, analyser),
            )
            if dbcurs.rowcount == 1:
                cur_source = dbcurs.fetchone()["id"]
                dbcurs.execute(
                    "INSERT INTO sources_password (source_id, password) VALUES (%s, %s);",
                    (cur_source, password),
                )
                print(
                    "inserted password=%s where country=%s analyser=%s"
                    % (password, country, analyser)
                )
                return

        if dbcurs.rowcount > 0:
            return

        if dbcurs.rowcount == 0:
            # otherwise, create a new entry in database
            print(
                "inserting country=%s analyser=%s source=%s password=%s"
                % (country, analyser, source, password)
            )
            try:
                dbcurs.execute(
                    "INSERT INTO sources (id, country, analyser) VALUES (%s, %s, %s);",
                    (source, country, analyser),
                )
                dbcurs.execute(
                    "INSERT INTO sources_password (source_id, password) VALUES (%s, %s);",
                    (source, password),
                )
                source += 1

            except psycopg2.IntegrityError:
                print(
                    "failure on country=%s analyser=%s password=%s"
                    % (country, analyser, password)
                )
                raise

        else:
            print(
                "updated country=%s analyser=%s where password=%s"
                % (country, analyser, password)
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

    importlib.reload(
        modules_legacy
    )  # needed as was loaded by import modules_legacy.utils
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

                        update_pass(country, analyser_name, password)

    dbconn.commit()
    dbconn.close()
