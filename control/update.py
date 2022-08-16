import json
import sys
import time
from typing import Dict, Optional
from xml.sax import handler, make_parser

import psycopg2

from modules.dependencies import database
from modules_legacy import utils

show = utils.show


class printlogger:
    def log(self, text):
        print(text)


class OsmoseUpdateAlreadyDone(Exception):
    pass


num_sql_run = 0


def execute_sql(dbcurs, sql: str, args=None):
    global num_sql_run
    try:
        if args is None:
            dbcurs.execute(sql)
        else:
            dbcurs.execute(sql, args)
    except Exception:
        print(sql, args)
        raise
    num_sql_run += 1
    if num_sql_run % 10000 == 0:
        print(".", end=" ")
        sys.stdout.flush()


def update(
    source_id: int,
    fname: str,
    logger: printlogger = printlogger(),
    remote_ip: Optional[str] = None,
):

    #  open connections
    dbconn = utils.get_dbconn()
    dbcurs = dbconn.cursor()

    #  xml parser
    parser = make_parser()
    parser.setContentHandler(update_parser(source_id, fname, remote_ip, dbconn, dbcurs))

    #  open the file
    if fname.endswith(".bz2"):
        import bz2

        f = bz2.BZ2File(fname)
    elif fname.endswith(".gz"):
        import gzip

        f = gzip.open(fname)
    else:
        f = open(fname)

    #  parse the file
    parser.parse(f)

    #  update subtitle from new errors
    execute_sql(
        dbcurs,
        """
UPDATE
  markers_status
SET
  subtitle = markers.subtitle
FROM
  markers
WHERE
  markers.source_id = %s AND
  markers_status.item = markers.item AND
  markers_status.uuid = markers.uuid
""",
        (source_id,),
    )

    #  #  remove false positive no longer present
    #    execute_sql(dbcurs, """DELETE FROM markers_status
    #                      WHERE (source_id,class,elems) NOT IN (SELECT source_id,class,elems FROM markers WHERE source_id = %s) AND
    #                            source_id = %s AND
    #                            date < now()-interval '7 day'""",
    #                   (source_id, source_id, ))

    execute_sql(
        dbcurs,
        """
DELETE FROM
  markers
USING
  markers_status
WHERE
  markers.source_id = %s AND
  markers_status.uuid = markers.uuid
""",
        (source_id,),
    )

    execute_sql(
        dbcurs,
        """UPDATE markers_counts
                      SET count = (SELECT count(*) FROM markers
                                   WHERE markers.source_id = markers_counts.source_id AND
                                         markers.class = markers_counts.class)
                      WHERE markers_counts.source_id = %s""",
        (source_id,),
    )

    #  commit and close
    dbconn.commit()
    dbconn.close()

    #  close and delete
    f.close()
    del f


class update_parser(handler.ContentHandler):
    def __init__(
        self, source_id: int, source_url: str, remote_ip: Optional[str], dbconn, dbcurs
    ):
        self._source_id = source_id
        self._source_url = source_url
        self._remote_ip = remote_ip
        self._dbconn = dbconn
        self._dbcurs = dbcurs
        self._class_item = {}
        self._tstamp_updated = False

        self.element_stack = []

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, name: str, attrs: Dict[str, str]):
        if name == "analyser":
            self.all_uuid = {}
            self.mode = "analyser"
            self.update_timestamp(attrs)

        elif name == "analyserChange":
            self.all_uuid = None
            self.mode = "analyserChange"
            self.update_timestamp(attrs)

        elif name == "error":
            self._class_id = int(attrs["class"])
            self._class_sub = int(attrs.get("subclass", "0"))
            self._error_elements = []
            self._error_locations = []
            self._error_texts = {}
            self._users = []
            self._fixes = []
            self.elem_mode = "info"
        elif name == "location":
            self._error_locations.append(dict(attrs))
        elif name == "text":
            self._error_texts[attrs["lang"]] = attrs["value"].replace("\n", "%%")

        elif name in ["node", "way", "relation", "infos"]:
            self._elem = dict(attrs)
            if "user" in self._elem:
                self._users.append(self._elem["user"])
            else:
                self._elem["user"] = None
            self._elem["type"] = name
            self._elem_tags = {}

            if self.elem_mode == "fix":
                self._fix_create = {}
                self._fix_modify = {}
                self._fix_delete = []

        elif name == "tag":
            if self.elem_mode == "info":
                self._elem_tags[attrs["k"]] = attrs["v"]
            elif self.elem_mode == "fix":
                if attrs["action"] == "create":
                    self._fix_create[attrs["k"]] = attrs["v"]
                elif attrs["action"] == "modify":
                    self._fix_modify[attrs["k"]] = attrs["v"]
                elif attrs["action"] == "delete":
                    self._fix_delete.append(attrs["k"])

        elif name == "class":
            self._class_id = int(attrs["id"])
            self._class_item[self._class_id] = int(attrs["item"])
            if "level" in attrs:
                self._class_level = int(attrs["level"])
            else:
                self._class_level = 2
            self._class_title = {}
            if "tag" in attrs:
                self._class_tags = attrs["tag"].split(",")
            else:
                self._class_tags = []
            self._class_source = attrs.get("source")
            self._class_resource = attrs.get("resource")

            self._class_title = {}
            self._class_detail = {}
            self._class_fix = {}
            self._class_trap = {}
            self._class_example = {}

        elif name == "classtext":
            self._class_title[attrs["lang"]] = attrs["title"]
        elif name == "detail":
            self._class_detail[attrs["lang"]] = attrs["title"]
        elif name == "fix" and self.element_stack[-1] == "class":
            self._class_fix[attrs["lang"]] = attrs["title"]
        elif name == "trap":
            self._class_trap[attrs["lang"]] = attrs["title"]
        elif name == "example":
            self._class_example[attrs["lang"]] = attrs["title"]
        elif name == "delete":
            # used by files generated with an .osc file
            execute_sql(
                self._dbcurs,
                """
DELETE FROM
    markers
WHERE
    source_id = %s AND
    ARRAY [%s::bigint] <@ marker_elem_ids(elems) AND
    (SELECT bool_or(elem->>\'type\' = %s AND elem->>\'id\' = %s) FROM (SELECT unnest(elems)) AS t(elem))
""",
                (
                    self._source_id,
                    str(attrs["id"]),
                    attrs["type"][0].upper(),
                    str(attrs["id"]),
                ),
            )

        elif name == "fixes":
            self.elem_mode = "fix"
        elif name == "fix" and self.element_stack[-1] == "fixes":
            self._fix = []
            self._fix_create = {}
            self._fix_modify = {}
            self._fix_delete = []

        self.element_stack.append(name)

    def endElement(self, name: str):
        self.element_stack.pop()

        if name == "analyser" and self.all_uuid:
            for class_id, uuid in self.all_uuid.items():
                execute_sql(
                    self._dbcurs,
                    "DELETE FROM markers WHERE source_id = %s AND class = %s AND uuid != ALL (%s::uuid[])",
                    (self._source_id, class_id, uuid),
                )

        elif name == "error":
            #  add data at all location
            if len(self._error_locations) == 0:
                print(
                    "No location on error found on line %d"
                    % self.locator.getLineNumber()
                )
                return

            elems = list(
                filter(
                    lambda e: e,
                    map(
                        lambda elem: dict(
                            filter(
                                lambda k_v: k_v[1],
                                {
                                    "type": elem["type"][0].upper(),
                                    "id": int(elem["id"]),
                                    "tags": elem["tag"],
                                    "username": elem["user"],
                                }.items(),
                            )
                        )
                        if elem["type"] in ("node", "way", "relation")
                        else dict(
                            filter(
                                lambda k_v: k_v[1],
                                {
                                    "tags": elem["tag"],
                                    "username": elem["user"],
                                }.items(),
                            )
                        )
                        if elem["type"] in ("infos")
                        else None,
                        self._error_elements,
                    ),
                )
            )

            fixes = list(
                map(
                    lambda fix: list(
                        map(
                            lambda elem: dict(
                                filter(
                                    lambda k_v: k_v[1],
                                    {
                                        "type": elem["type"][0].upper(),
                                        "id": int(elem["id"]),
                                        "create": elem["create"],
                                        "modify": elem["modify"],
                                        "delete": elem["delete"],
                                    }.items(),
                                )
                            ),
                            filter(
                                lambda elem: elem["type"]
                                in ("node", "way", "relation"),
                                fix,
                            ),
                        )
                    ),
                    self._fixes,
                )
            )

            sql_uuid = "SELECT ('{' || encode(substring(digest(%(source)s || '/' || %(class)s || '/' || %(subclass)s || '/' || %(elems_sig)s, 'sha256') from 1 for 16), 'hex') || '}')::uuid AS uuid"

            #  sql template
            sql_marker = """
INSERT INTO markers (uuid, source_id, class, item, lat, lon, elems, fixes, subtitle)
VALUES (
    ('{' || encode(substring(digest(%(source)s || '/' || %(class)s || '/' || %(subclass)s || '/' || %(elems_sig)s, 'sha256') from 1 for 16), 'hex') || '}')::uuid,
    %(source)s,
    %(class)s,
    %(item)s,
    %(lat)s,
    %(lon)s,
    %(elems)s::jsonb[],
    %(fixes)s::jsonb[],
    %(subtitle)s
)
ON CONFLICT (uuid) DO
UPDATE SET
    item = %(item)s,
    lat = %(lat)s,
    lon = %(lon)s,
    elems = %(elems)s::jsonb[],
    fixes = %(fixes)s::jsonb[],
    subtitle = %(subtitle)s
WHERE
    markers.uuid = ('{' || encode(substring(digest(%(source)s || '/' || %(class)s || '/' || %(subclass)s || '/' || %(elems_sig)s, 'sha256') from 1 for 16), 'hex') || '}')::uuid AND
    markers.source_id = %(source)s AND
    markers.class = %(class)s AND
    (
        markers.item IS DISTINCT FROM %(item)s OR
        markers.lat IS DISTINCT FROM %(lat)s OR
        markers.lon IS DISTINCT FROM %(lon)s OR
        markers.elems IS DISTINCT FROM %(elems)s::jsonb[] OR
        markers.fixes IS DISTINCT FROM %(fixes)s::jsonb[] OR
        markers.subtitle IS DISTINCT FROM %(subtitle)s
    )
RETURNING uuid
"""

            for location in self._error_locations:
                lat = float(location["lat"])
                lon = float(location["lon"])

                params = {
                    "source": self._source_id,
                    "class": self._class_id,
                    "subclass": self._class_sub,
                    "item": self._class_item[self._class_id],
                    "lat": lat,
                    "lon": lon,
                    "elems_sig": "_".join(
                        map(
                            lambda elem: elem["type"] + str(elem["id"]),
                            self._error_elements,
                        )
                    ),
                    "elems": list(map(lambda elem: json.dumps(elem), elems))
                    if elems
                    else None,
                    "fixes": list(map(lambda fix: json.dumps(fix), fixes))
                    if fixes
                    else None,
                    "subtitle": self._error_texts,
                }

                execute_sql(self._dbcurs, sql_uuid, params)
                r = self._dbcurs.fetchone()
                if r and r[0] and self.all_uuid is not None:
                    self.all_uuid[self._class_id].append(r[0])

                execute_sql(self._dbcurs, sql_marker, params)
                self._dbcurs.fetchone()

        elif name in ["node", "way", "relation", "infos"]:
            if self.elem_mode == "info":
                self._elem["tag"] = self._elem_tags
                self._error_elements.append(self._elem)
            else:
                self._elem["create"] = self._fix_create
                self._elem["modify"] = self._fix_modify
                self._elem["delete"] = self._fix_delete
                self._fix.append(self._elem)

        elif name == "class":
            if self.all_uuid is not None:
                self.all_uuid[self._class_id] = []

            # Commit class update on its own transaction. Avoid lock the class table and block other updates.
            try:
                db_local = database.get_dbconn()
                db_local.execute(
                    """
INSERT INTO class (class, item, title, level, tags, detail, fix, trap, example, source, resource, timestamp)
VALUES
    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)
ON CONFLICT (item, class) DO
UPDATE SET
        title = $3,
        level = $4,
        tags = $5,
        detail = $6,
        fix = $7,
        trap = $8,
        example = $9,
        source = $10,
        resource = $11,
        timestamp = $12
WHERE
    class.class = $1 AND
    class.item = $2 AND
    class.timestamp < $12 AND
    (
        class.title IS DISTINCT FROM $3 OR
        class.level IS DISTINCT FROM $4 OR
        class.tags IS DISTINCT FROM $5::varchar[] OR
        class.detail IS DISTINCT FROM $6 OR
        class.fix IS DISTINCT FROM $7 OR
        class.trap IS DISTINCT FROM $8 OR
        class.example IS DISTINCT FROM $9 OR
        class.source IS DISTINCT FROM $10 OR
        class.resource IS DISTINCT FROM $11
    )
""",
                    self._class_id,  # $1 class
                    self._class_item[self._class_id],  # $2 item
                    self._class_title,  # $3 title
                    self._class_level,  # $4 level
                    self._class_tags,  # $5 tags
                    self._class_detail or None,  # $6 detail
                    self._class_fix or None,  # $7 fix
                    self._class_trap or None,  # $8 trap
                    self._class_example or None,  # $9 example
                    self._class_source or None,  # $10 source
                    self._class_resource or None,  # $11 resource
                    self.ts,  # $12 timestamp
                )
            finally:
                db_local.close()

            sql = """
INSERT INTO markers_counts (source_id, class, item)
VALUES (%(source)s, %(class)s, %(item)s)
ON CONFLICT (source_id, class) DO
UPDATE SET
    item = %(item)s
WHERE
    markers_counts.source_id = %(source)s AND
    markers_counts.class = %(class)s
"""
            execute_sql(
                self._dbcurs,
                sql,
                {
                    "source": self._source_id,
                    "class": self._class_id,
                    "item": self._class_item[self._class_id],
                },
            )

        elif name == "fixes":
            self.elem_mode = "info"
        elif name == "fix" and self.element_stack[-1] == "fixes":
            self._fixes.append(self._fix)

    def update_timestamp(self, attrs: Dict[str, str]):
        self.ts = attrs.get(
            "timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        )
        self.version = attrs.get("version", None)
        self.analyser_version = attrs.get("analyser_version", None)

        if not self._tstamp_updated:
            try:
                execute_sql(
                    self._dbcurs,
                    "INSERT INTO updates (source_id, timestamp, remote_url, remote_ip, version, analyser_version) VALUES(%s, %s, %s, %s, %s, %s);",
                    (
                        self._source_id,
                        utils.pg_escape(self.ts),
                        utils.pg_escape(self._source_url),
                        utils.pg_escape(self._remote_ip),
                        utils.pg_escape(self.version),
                        utils.pg_escape(self.analyser_version),
                    ),
                )
            except psycopg2.IntegrityError:
                self._dbconn.rollback()
                execute_sql(
                    self._dbcurs,
                    'SELECT count(*) FROM updates WHERE source_id = %s AND "timestamp" = %s',
                    (self._source_id, utils.pg_escape(self.ts)),
                )
                r = self._dbcurs.fetchone()
                if r["count"] == 1:
                    raise OsmoseUpdateAlreadyDone(
                        "source=%s and timestamp=%s are already present"
                        % (self._source_id, utils.pg_escape(self.ts))
                    )
                else:
                    raise

            execute_sql(
                self._dbcurs,
                "UPDATE updates_last SET timestamp=%s, version=%s, analyser_version=%s, remote_ip=%s WHERE source_id=%s;",
                (
                    utils.pg_escape(self.ts),
                    utils.pg_escape(self.version),
                    utils.pg_escape(self.analyser_version),
                    utils.pg_escape(self._remote_ip),
                    self._source_id,
                ),
            )
            if self._dbcurs.rowcount == 0:
                execute_sql(
                    self._dbcurs,
                    "INSERT INTO updates_last(source_id, timestamp, version, analyser_version, remote_ip) VALUES(%s, %s, %s, %s, %s);",
                    (
                        self._source_id,
                        utils.pg_escape(self.ts),
                        utils.pg_escape(self.version),
                        utils.pg_escape(self.analyser_version),
                        utils.pg_escape(self._remote_ip),
                    ),
                )

            self._tstamp_updated = True


def print_source(source: Dict[str, str]):
    show("source #%s" % source["id"])
    for k in source:
        if k == "id":
            continue
        if type(source[k]) == list:
            for e in source[k]:
                show("   %-10s = %s" % (k, e))
        else:
            show("   %-10s = %s" % (k, source[k]))


import unittest


class Test(unittest.TestCase):
    def setUp(self):
        utils.pg_host = "localhost"
        utils.pg_base = "osmose_test"
        utils.pg_pass = "-osmose-"
        utils.db_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (
            utils.pg_host,
            utils.pg_port,
            utils.pg_base,
            utils.pg_user,
            utils.pg_pass,
        )

        self.dbconn = utils.get_dbconn()
        self.dbcurs = self.dbconn.cursor()
        self.dbcurs.execute(open("tools/database/drop.sql", "r").read())
        self.dbcurs.execute(open("tools/database/schema.sql", "r").read())
        #  Re-initialise search_path as cleared by schema.sql
        self.dbcurs.execute('SET search_path TO "$user", public;')
        self.dbcurs.execute(
            "INSERT INTO sources (id, country, analyser) VALUES (%s, %s, %s);",
            (1, "xx1", "yy1"),
        )
        self.dbcurs.execute(
            "INSERT INTO sources (id, country, analyser) VALUES (%s, %s, %s);",
            (2, "xx2", "yy2"),
        )
        self.dbcurs.execute(
            "INSERT INTO sources_password (source_id, password) VALUES (%s, %s);",
            (1, "xx1"),
        )
        self.dbcurs.execute(
            "INSERT INTO sources_password (source_id, password) VALUES (%s, %s);",
            (2, "xx2"),
        )
        self.dbconn.commit()

    def tearDown(self):
        self.dbconn.close()

    def check_num_marker(self, num):
        self.dbcurs.execute("SELECT count(*) FROM markers")
        cur_num = self.dbcurs.fetchone()[0]
        self.assertEquals(num, cur_num)

    def test(self):
        self.check_num_marker(0)
        update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

    def test_update(self):
        self.check_num_marker(0)
        update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-05-20.xml.bz2")
        self.check_num_marker(48)

        update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

    def test_duplicate_update(self):
        self.check_num_marker(0)
        update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

        with self.assertRaises(OsmoseUpdateAlreadyDone):
            update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

    def test_two_sources(self):
        self.check_num_marker(0)
        update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

        update(
            2,
            "tests/Analyser_Osmosis_Broken_Highway_Level_Continuity-france_reunion-2014-06-11.xml.bz2",
        )
        self.check_num_marker(50 + 99)


if __name__ == "__main__":
    sources = utils.get_sources()
    if len(sys.argv) == 1:
        for k in sorted([int(x) for x in sources.keys()]):
            source = sources[str(k)]
            print_source(source)
    elif sys.argv[1] == "--help":
        show("usage: update.py <source number> <url>")
    else:
        update(utils.get_sources()[sys.argv[1]], sys.argv[2])
