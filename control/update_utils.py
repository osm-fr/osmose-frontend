import asyncio
import bz2
import gzip
import sys
import time
import unittest
from typing import Any, Dict, List, Optional
from xml.sax import handler, make_parser

import dateutil.parser
from asyncpg import Connection

from modules import query_meta, utils
from modules.dependencies import database

Elem = Dict[str, Any]
Fix = Elem

show = utils.show


class printlogger:
    def log(self, text: str) -> None:
        print(text)


class OsmoseUpdateAlreadyDone(Exception):
    pass


async def update(
    db: Connection,
    source_id: int,
    fname: str,
    logger: printlogger = printlogger(),
    remote_ip: Optional[str] = None,
) -> None:
    q: asyncio.Queue = asyncio.Queue()

    async def sync_parser():
        #  xml parser
        parser = make_parser()
        parser.setContentHandler(update_parser(q))

        #  open the file
        if fname.endswith(".bz2"):
            f = bz2.BZ2File(fname)
        elif fname.endswith(".gz"):
            f = gzip.open(fname)
        else:
            f = open(fname)

        #  parse the file
        parser.parse(f)

        #  close and delete
        f.close()
        del f

    async def async_parser():
        await async_update_parser(source_id, fname, remote_ip, db).parse(q)

    tasks = [
        asyncio.create_task(sync_parser()),
        asyncio.create_task(async_parser()),
    ]
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_EXCEPTION)

    for task in pending:
        task.cancel()

    if not tasks[0].cancelled():
        e = tasks[0].exception()
        if e:
            raise e
    if not tasks[1].cancelled():
        e = tasks[1].exception()
        if e:
            raise e

    #  update subtitle from new errors
    await db.execute(
        """
UPDATE
  markers_status
SET
  subtitle = markers.subtitle
FROM
  markers
WHERE
  markers.source_id = $1 AND
  markers_status.item = markers.item AND
  markers_status.uuid = markers.uuid
""",
        source_id,
    )

    #     #  remove false positive no longer present
    #     await db.execute(
    #         """
    # DELETE FROM
    #     markers_status
    # WHERE
    #     (source_id, class, elems) NOT IN (
    #         SELECT
    #             source_id,
    #             class,
    #             elems
    #         FROM
    #             markers
    #         WHERE
    #             source_id = $1
    #     ) AND
    #     source_id = $2 AND
    #     date < now()-interval '7 day'
    # """,
    #         source_id,
    #         source_id,
    #     )

    await db.execute(
        """
DELETE FROM
  markers
USING
  markers_status
WHERE
  markers.source_id = $1 AND
  markers_status.uuid = markers.uuid
""",
        source_id,
    )

    await db.execute(
        """
UPDATE
    markers_counts
SET
    count = (
        SELECT
            count(*)
        FROM
            markers
        WHERE
            markers.source_id = markers_counts.source_id AND
            markers.class = markers_counts.class
    )
WHERE
    markers_counts.source_id = $1
""",
        source_id,
    )


async def update_class(
    _db: Connection,
    _source_id: int,
    _class_id: int,
    _class_item: int,
    _class_title: Dict[str, str],
    _class_level: int,
    _class_tags: List[str],
    _class_detail: Optional[Dict[str, str]],
    _class_fix: Optional[Dict[str, str]],
    _class_trap: Optional[Dict[str, str]],
    _class_example: Optional[Dict[str, str]],
    _class_source: Optional[str],
    _class_resource: Optional[str],
    ts: float,
) -> None:
    # Commit class update on its own transaction. Avoid lock the class table and block other updates.
    # db_local: Connection = await database.db().__anext__()
    db_local = _db
    await db_local.execute(
        """
INSERT INTO class (class, item, title, level, tags, detail, fix, trap, example, source, resource, timestamp)
VALUES
    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, to_timestamp($12))
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
        timestamp = to_timestamp($12)
WHERE
    class.class = $1 AND
    class.item = $2 AND
    class.timestamp < to_timestamp($12) AND
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
        _class_id,  # $1 class
        _class_item,  # $2 item
        _class_title,  # $3 title
        _class_level,  # $4 level
        _class_tags,  # $5 tags
        _class_detail or None,  # $6 detail
        _class_fix or None,  # $7 fix
        _class_trap or None,  # $8 trap
        _class_example or None,  # $9 example
        _class_source or None,  # $10 source
        _class_resource or None,  # $11 resource
        ts,  # $12 timestamp
    )

    sql = """
INSERT INTO markers_counts (source_id, class, item)
VALUES ($1, $2, $3)
ON CONFLICT (source_id, class) DO
UPDATE SET
    item = $3
WHERE
    markers_counts.source_id = $1 AND
    markers_counts.class = $2
"""
    await _db.execute(
        sql,
        _source_id,  # $1 source
        _class_id,  # $2 class
        _class_item,  # $3 item
    )


async def update_issue(
    _db: Connection,
    all_uuid: Optional[Dict[int, List[str]]],
    _error_locations: List[Dict[str, str]],
    _source_id: int,
    _class_id: int,
    _class_sub: int,
    _class_item: int,
    _error_elements: List[Elem],
    elems: List[Optional[Elem]],
    fixes: List[List[Fix]],
    _error_texts: Optional[Dict[str, str]],
) -> None:
    uuid = """('{' ||
        encode(substring(digest(
            $1::int ||
            '/' ||
            $2::int ||
            '/' ||
            $3::bigint ||
            '/' ||
            $4, 'sha256'
        ) from 1 for 16), 'hex') ||
    '}')::uuid"""
    sql_uuid = "SELECT " + uuid + " AS uuid"

    #  sql template
    sql_marker = (
        """
INSERT INTO markers (uuid, source_id, class, item, lat, lon, elems, fixes, subtitle)
VALUES (
    """
        + uuid
        + """,
    $1, $2, $5, $6, $7,
    -- Hack to pass variable json struct on asyncio params
    (SELECT array_agg(j) FROM jsonb_array_elements($8::jsonb) AS t(j)),
    (SELECT array_agg(j) FROM jsonb_array_elements($9::jsonb) AS t(j)),
    $10
)
ON CONFLICT (uuid) DO
UPDATE SET
    item = $5,
    lat = $6,
    lon = $7,
    elems = (SELECT array_agg(j) FROM jsonb_array_elements($8::jsonb) AS t(j)),
    fixes = (SELECT array_agg(j) FROM jsonb_array_elements($9::jsonb) AS t(j)),
    subtitle = $10
WHERE
    markers.uuid = """
        + uuid
        + """ AND
    markers.source_id = $1 AND
    markers.class = $2 AND
    (
        markers.item IS DISTINCT FROM $5 OR
        markers.lat IS DISTINCT FROM $6 OR
        markers.lon IS DISTINCT FROM $7 OR
        markers.elems IS DISTINCT FROM (SELECT array_agg(j) FROM jsonb_array_elements($8::jsonb) AS t(j)) OR
        markers.fixes IS DISTINCT FROM (SELECT array_agg(j) FROM jsonb_array_elements($9::jsonb) AS t(j)) OR
        markers.subtitle IS DISTINCT FROM $10
    )
"""
    )

    for location in _error_locations:
        lat = float(location["lat"])
        lon = float(location["lon"])

        params = [
            _source_id,  # $1 source
            _class_id,  # $2 class
            _class_sub,  # $3 subclass
            "_".join(
                map(
                    lambda elem: elem["type"] + str(elem["id"]),
                    _error_elements,
                )
            ),  # $4 elems_sig
        ]
        r = await _db.fetchval(sql_uuid, *params)
        if r and all_uuid is not None:
            all_uuid[_class_id].append(r)

        params += [
            _class_item,  # $5 item
            lat,  # $6 lat
            lon,  # $7 lon
            elems if elems else None,  # $8 elems
            fixes if fixes else None,  # $9 fixes
            _error_texts,  # $10 subtitle
        ]
        await _db.execute(sql_marker, *params)


class update_parser(handler.ContentHandler):
    def __init__(self, q: asyncio.Queue):
        self.q = q

    def put(self, args: List[Any]):
        done = False
        while not done:
            try:
                self.q.put_nowait(args)
                done = True
            except asyncio.QueueFull:
                time.sleep(0.05)
                continue

    def setDocumentLocator(self, *args) -> None:
        self.put(["setDocumentLocator", *args])

    def startElement(self, *args) -> None:
        self.put(["startElement", *args])

    def endElement(self, *args) -> None:
        self.put(["endElement", *args])

    def endDocument(self) -> None:
        self.put(["endDocument"])


class async_update_parser(handler.ContentHandler):
    _source_id: int
    _source_url: str
    _remote_ip: Optional[str]
    _class_item: Dict[int, int]
    _tstamp_updated: bool
    all_uuid: Optional[Dict[int, List[str]]]
    mode: str

    element_stack: List[str]

    _class_id: int
    _class_sub: int
    _error_elements: List[Elem]
    _error_locations: List[Dict[str, str]]
    _error_texts: Dict[str, str]
    _users: List[str]
    _fixes: List[List[Fix]]
    _fix: List[Fix]
    elem_mode: str

    _elem: Elem

    _fix_create: Dict[str, str]
    _fix_modify: Dict[str, str]
    _fix_delete: List[str]

    _class_title: Dict[str, str]

    def __init__(
        self,
        source_id: int,
        source_url: str,
        remote_ip: Optional[str],
        db: Connection,
    ):
        self._source_id = source_id
        self._source_url = source_url
        self._remote_ip = remote_ip
        self._db = db
        self._class_item = {}
        self._tstamp_updated = False

        self.element_stack = []

    async def parse(self, q: asyncio.Queue) -> None:
        while True:
            a = await q.get()
            f = a[0]
            args = a[1:]
            if f == "setDocumentLocator":
                await self.setDocumentLocator(*args)
            elif f == "startElement":
                await self.startElement(*args)
            elif f == "endElement":
                await self.endElement(*args)
            q.task_done()

            if f == "endDocument":
                break

    async def setDocumentLocator(self, locator) -> None:
        self.locator = locator

    async def startElement(self, name: str, attrs: Dict[str, str]) -> None:
        if name == "analyser":
            self.all_uuid = {}
            self.mode = "analyser"
            await self.update_timestamp(attrs)

        elif name == "analyserChange":
            self.all_uuid = None
            self.mode = "analyserChange"
            await self.update_timestamp(attrs)

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
            await self._db.execute(
                """
DELETE FROM
    markers
WHERE
    source_id = $1 AND
    ARRAY [$2::bigint] <@ marker_elem_ids(elems) AND
    (SELECT bool_or(elem->>\'type\' = $3 AND elem->>\'id\' = $4) FROM (SELECT unnest(elems)) AS t(elem))
""",
                self._source_id,
                int(attrs["id"]),
                attrs["type"][0].upper(),
                str(attrs["id"]),
            )

        elif name == "fixes":
            self.elem_mode = "fix"
        elif name == "fix" and self.element_stack[-1] == "fixes":
            self._fix = []
            self._fix_create = {}
            self._fix_modify = {}
            self._fix_delete = []

        self.element_stack.append(name)

    async def endElement(self, name: str) -> None:
        self.element_stack.pop()

        if name == "analyser" and self.all_uuid:
            for class_id, uuid in self.all_uuid.items():
                await self._db.execute(
                    "DELETE FROM markers WHERE source_id = $1 AND class = $2 AND uuid != ALL ($3::uuid[])",
                    self._source_id,
                    class_id,
                    uuid,
                )

        elif name == "error":
            #  add data at all location
            if len(self._error_locations) == 0:
                print(
                    f"No location on error found on line {self.locator.getLineNumber()}"
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

            await update_issue(
                self._db,
                self.all_uuid,
                self._error_locations,
                self._source_id,
                self._class_id,
                self._class_sub,
                self._class_item[self._class_id],
                self._error_elements,
                elems,
                fixes,
                self._error_texts,
            )

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

            await update_class(
                self._db,
                self._source_id,
                self._class_id,
                self._class_item[self._class_id],
                self._class_title,
                self._class_level,
                self._class_tags,
                self._class_detail or None,
                self._class_fix or None,
                self._class_trap or None,
                self._class_example or None,
                self._class_source or None,
                self._class_resource or None,
                self.ts,
            )

        elif name == "fixes":
            self.elem_mode = "info"
        elif name == "fix" and self.element_stack[-1] == "fixes":
            self._fixes.append(self._fix)

    async def update_timestamp(self, attrs: Dict[str, str]) -> None:
        timestamp = attrs.get("timestamp")
        if timestamp:
            self.ts = dateutil.parser.isoparse(timestamp).timestamp()
        else:
            self.ts = time.time()

        self.version = attrs.get("version", None)
        self.analyser_version = attrs.get("analyser_version", None)

        if not self._tstamp_updated:
            r = await self._db.fetchval(
                """
INSERT INTO updates
    (source_id, timestamp, remote_url, remote_ip, version, analyser_version)
VALUES
    ($1, to_timestamp($2), $3, $4, $5, $6)
ON CONFLICT DO NOTHING
RETURNING 1
""",
                self._source_id,
                self.ts,
                self._source_url,
                self._remote_ip,
                self.version,
                self.analyser_version,
            )

            if not r:
                raise OsmoseUpdateAlreadyDone(
                    f"source={self._source_id} and timestamp={self.ts} are already present"
                )

            await self._db.execute(
                """
INSERT INTO updates_last
    (source_id, timestamp, version, analyser_version, remote_ip)
VALUES
    ($1, to_timestamp($2), $3, $4, $5)
ON CONFLICT (source_id) DO
UPDATE SET
    timestamp=to_timestamp($2),
    version=$3,
    analyser_version=$4,
    remote_ip=$5
WHERE
    updates_last.source_id=$1
""",
                self._source_id,
                self.ts,
                self.version,
                self.analyser_version,
                self._remote_ip,
            )

            self._tstamp_updated = True


def print_source(source: Dict[str, str]) -> None:
    show(f"source #{source['id']}")
    for k in source:
        if k == "id":
            continue
        if type(source[k]) == list:
            for e in source[k]:
                show("   %-10s = %s" % (k, e))
        else:
            show("   %-10s = %s" % (k, source[k]))


class Test(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        utils.pg_host = "localhost"
        utils.pg_base = "osmose_test"
        utils.pg_pass = "-osmose-"

        self.db = await database.get_dbconn()

        with open("tools/database/drop.sql", "r") as f:
            await self.db.execute(f.read())
        with open("tools/database/schema.sql", "r") as f:
            await self.db.execute(f.read())
        #  Re-initialise search_path as cleared by schema.sql
        await self.db.execute('SET search_path TO "$user", public;')
        await self.db.execute(
            "INSERT INTO sources (id, country, analyser) VALUES ($1, $2, $3);",
            1,
            "xx1",
            "yy1",
        )
        await self.db.execute(
            "INSERT INTO sources (id, country, analyser) VALUES ($1, $2, $3);",
            2,
            "xx2",
            "yy2",
        )
        await self.db.execute(
            "INSERT INTO sources_password (source_id, password) VALUES ($1, $2);",
            1,
            "xx1",
        )
        await self.db.execute(
            "INSERT INTO sources_password (source_id, password) VALUES ($1, $2);",
            2,
            "xx2",
        )

    async def asyncTearDown(self):
        await self.db.close()

    async def check_num_marker(self, num):
        cur_num = await self.db.fetchval("SELECT count(*) FROM markers")
        self.assertEqual(num, cur_num)

    async def test(self):
        await self.check_num_marker(0)
        await update(
            self.db,
            1,
            "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2",
        )
        await self.check_num_marker(50)

    async def test_update(self):
        await self.check_num_marker(0)
        await update(
            self.db,
            1,
            "tests/Analyser_Osmosis_Soundex-france_alsace-2014-05-20.xml.bz2",
        )
        await self.check_num_marker(48)

        await update(
            self.db,
            1,
            "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2",
        )
        await self.check_num_marker(50)

    async def test_duplicate_update(self):
        await self.check_num_marker(0)
        await update(
            self.db,
            1,
            "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2",
        )
        await self.check_num_marker(50)

        with self.assertRaises(OsmoseUpdateAlreadyDone):
            await update(
                self.db,
                1,
                "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2",
            )
        await self.check_num_marker(50)

    async def test_two_sources(self):
        await self.check_num_marker(0)
        await update(
            self.db,
            1,
            "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2",
        )
        await self.check_num_marker(50)

        await update(
            self.db,
            2,
            "tests/Analyser_Osmosis_Broken_Highway_Level_Continuity-france_reunion-2014-06-11.xml.bz2",
        )
        # Including 12 duplicates
        await self.check_num_marker(50 + 99 - 12)


async def main():
    if sys.argv[1] == "--help":
        show("usage: update.py <source number> <url>")
    else:
        db = database.get_dbconn()
        sources = await query_meta._sources(db)
        if len(sys.argv) == 1:
            for k in sorted([int(x) for x in sources.keys()]):
                source = sources[str(k)]
                print_source(source)
        else:
            await update(db, sources[sys.argv[1]], sys.argv[2])


if __name__ == "__main__":
    asyncio.run(main())
