#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

import sys, time
import psycopg2
from modules import utils
import json
from xml.sax import make_parser, handler

show = utils.show

###########################################################################
## logger

class printlogger:
    def log(self, text):
        print(text)

###########################################################################
## updater

class OsmoseUpdateAlreadyDone(Exception):
    pass

num_sql_run = 0

def execute_sql(dbcurs, sql, args = None):
    global num_sql_run
    try:
        if args == None:
            dbcurs.execute(sql)
        else:
            dbcurs.execute(sql, args)
    except:
        print(sql, args)
        raise
    num_sql_run += 1
    if num_sql_run % 10000 == 0:
        print(".", end=' ')
        sys.stdout.flush()

def update(source_id, fname, logger = printlogger(), remote_ip=""):

    ## open connections
    dbconn = utils.get_dbconn()
    dbcurs = dbconn.cursor()

    ## xml parser
    parser = make_parser()
    parser.setContentHandler(update_parser(source_id, fname, remote_ip, dbconn, dbcurs))

    ## open the file
    if fname.endswith(".bz2"):
        import bz2
        f = bz2.BZ2File(fname)
    elif fname.endswith(".gz"):
        import gzip
        f = gzip.open(fname)
    else:
        f = open(fname)

    ## parse the file
    parser.parse(f)

    ## update subtitle from new errors
    execute_sql(dbcurs, """
UPDATE
  dynpoi_status
SET
  subtitle = marker.subtitle
FROM
  marker
WHERE
  marker.source = %s AND
  dynpoi_status.uuid = marker.uuid
""", (source_id, ))

    ## remove false positive no longer present
#    execute_sql(dbcurs, """DELETE FROM dynpoi_status
#                      WHERE (source,class,elems) NOT IN (SELECT source,class,elems FROM marker WHERE source = %s) AND
#                            source = %s AND
#                            date < now()-interval '7 day'""",
#                   (source_id, source_id, ))

    execute_sql(dbcurs, """
DELETE FROM
  marker
USING
  dynpoi_status
WHERE
  marker.source = %s AND
  dynpoi_status.uuid = marker.uuid
""", (source_id, ))

    execute_sql(dbcurs, """UPDATE dynpoi_class
                      SET count = (SELECT count(*) FROM marker
                                   WHERE marker.source = dynpoi_class.source AND
                                         marker.class = dynpoi_class.class)
                      WHERE dynpoi_class.source = %s""",
                   (source_id, ))

    ## commit and close
    dbconn.commit()
    dbconn.close()

    ## close and delete
    f.close()
    del f

class update_parser(handler.ContentHandler):

    def __init__(self, source_id, source_url, remote_ip, dbconn, dbcurs):
        self._source_id        = source_id
        self._source_url       = source_url
        self._remote_ip        = remote_ip
        self._dbconn           = dbconn
        self._dbcurs           = dbcurs
        self._class_item       = {}
        self._tstamp_updated   = False

        self.element_stack = []

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, name, attrs):
        if name == u"analyser":
            self.all_uuid = {}
            self.mode = "analyser"
            self.update_timestamp(attrs)

        elif name == u"analyserChange":
            self.mode = "analyserChange"
            self.update_timestamp(attrs)

        elif name == u"error":
            self._class_id        = int(attrs["class"])
            self._class_sub       = int(attrs.get("subclass", u"0"))
            self._error_elements  = []
            self._error_locations = []
            self._error_texts     = {}
            self._users           = []
            self._fixes           = []
            self.elem_mode        = "info"
        elif name == u"location":
            self._error_locations.append(dict(attrs))
        elif name == u"text":
            self._error_texts[attrs["lang"]] = attrs["value"].replace("\n", "%%")

        elif name in [u"node", u"way", u"relation", u"infos"]:
            self._elem = dict(attrs)
            if "user" in self._elem:
                self._users.append(self._elem["user"])
            else:
                self._elem["user"] = None
            self._elem[u"type"] = name
            self._elem_tags = {}

            if self.elem_mode == "fix":
                self._fix_create = {}
                self._fix_modify = {}
                self._fix_delete = []

        elif name == u"tag":
            if self.elem_mode == "info":
               self._elem_tags[attrs["k"]] = attrs["v"]
            elif self.elem_mode == "fix":
               if attrs["action"] == "create":
                  self._fix_create[attrs["k"]] = attrs["v"]
               elif attrs["action"] == "modify":
                  self._fix_modify[attrs["k"]] = attrs["v"]
               elif attrs["action"] == "delete":
                  self._fix_delete.append(attrs["k"])


        elif name == u"class":
            self._class_id    = int(attrs["id"])
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

            self._class_title      = {}
            self._class_detail     = {}
            self._class_fix        = {}
            self._class_trap       = {}
            self._class_example    = {}

        elif name == u"classtext":
            self._class_title[attrs["lang"]] = attrs["title"]
        elif name == u"detail":
            self._class_detail[attrs["lang"]] = attrs["title"]
        elif name == u"fix" and self.element_stack[-1] == u"class":
            self._class_fix[attrs["lang"]] = attrs["title"]
        elif name == u"trap":
            self._class_trap[attrs["lang"]] = attrs["title"]
        elif name == u"example":
            self._class_example[attrs["lang"]] = attrs["title"]
        elif name == u"delete":
            # used by files generated with an .osc file
            execute_sql(self._dbcurs, """
DELETE FROM
    marker
WHERE
    source = %s AND
    (SELECT bool_or(elem->\'type\' = \'"%s"\'::jsonb AND elem->\'id\' = \'%s\'::jsonb) FROM (SELECT unnest(elems)) AS t(elem))
""", (self._source_id, attrs["type"][0].upper(), attrs["id"]))

        elif name == u"fixes":
            self.elem_mode = "fix"
        elif name == u"fix" and self.element_stack[-1] == u"fixes":
            self._fix = []
            self._fix_create = {}
            self._fix_modify = {}
            self._fix_delete = []

        self.element_stack.append(name)


    def endElement(self, name):
        self.element_stack.pop()

        if name == u"analyser":
            for class_id, uuid in self.all_uuid.items():
                execute_sql(self._dbcurs, "DELETE FROM marker WHERE source = %s AND class = %s AND uuid != ALL (%s::uuid[])", (self._source_id, class_id, uuid))

        elif name == u"error":
            ## add data at all location
            if len(self._error_locations) == 0:
                print("No location on error found on line %d" % self.locator.getLineNumber())
                return

            elems = list(filter(lambda e: e, map(lambda elem: dict(filter(lambda k_v: k_v[1], {
                    'type': elem['type'][0].upper(),
                    'id': int(elem['id']),
                    'tags': elem['tag'],
                    'username': elem['user'],
                }.items())) if elem['type'] in ('node', 'way', 'relation') else dict(filter(lambda k_v: k_v[1], {
                    'tags': elem['tag'],
                    'username': elem['user'],
                }.items())) if elem['type'] in ('infos') else
                None,
                self._error_elements
            )))

            fixes = list(map(lambda fix:
                list(map(lambda elem: dict(filter(lambda k_v: k_v[1], {
                    'type': elem['type'][0].upper(),
                    'id': int(elem['id']),
                    'create': elem['create'],
                    'modify': elem['modify'],
                    'delete': elem['delete'],
                }.items())), filter(lambda elem: elem['type'] in ('node', 'way', 'relation'), fix))),
                self._fixes
            ))

            sql_uuid = u"SELECT ('{' || encode(substring(digest(%(source)s || '/' || %(class)s || '/' || %(subclass)s || '/' || %(elems_sig)s, 'sha256') from 1 for 16), 'hex') || '}')::uuid AS uuid"

            ## sql template
            sql_marker = u"INSERT INTO marker (uuid, source, class, item, lat, lon, elems, fixes, subtitle) "
            sql_marker += u"VALUES (('{' || encode(substring(digest(%(source)s || '/' || %(class)s || '/' || %(subclass)s || '/' || %(elems_sig)s, 'sha256') from 1 for 16), 'hex') || '}')::uuid, "
            sql_marker += u"%(source)s, %(class)s, %(item)s, %(lat)s, %(lon)s, %(elems)s::jsonb[], %(fixes)s::jsonb[], %(subtitle)s) "
            sql_marker += u"ON CONFLICT (uuid) DO "
            sql_marker += u"UPDATE SET item = %(item)s, lat = %(lat)s, lon = %(lon)s, elems = %(elems)s::jsonb[], fixes = %(fixes)s::jsonb[], subtitle = %(subtitle)s "
            sql_marker += u"WHERE marker.uuid = ('{' || encode(substring(digest(%(source)s || '/' || %(class)s || '/' || %(subclass)s || '/' || %(elems_sig)s, 'sha256') from 1 for 16), 'hex') || '}')::uuid AND "
            sql_marker += u"      marker.source = %(source)s AND marker.class = %(class)s AND "
            sql_marker += u"      (marker.item IS DISTINCT FROM %(item)s OR marker.lat IS DISTINCT FROM %(lat)s OR marker.lon IS DISTINCT FROM %(lon)s OR marker.elems IS DISTINCT FROM %(elems)s::jsonb[] OR marker.fixes IS DISTINCT FROM %(fixes)s::jsonb[] OR marker.subtitle IS DISTINCT FROM %(subtitle)s) "
            sql_marker += u"RETURNING uuid"

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
                    "elems_sig": '_'.join(map(lambda elem: elem['type'] + str(elem['id']), self._error_elements)),
                    "elems": list(map(lambda elem: json.dumps(elem), elems)) if elems else None,
                    "fixes": list(map(lambda fix: json.dumps(fix), fixes)) if fixes else None,
                    "subtitle": self._error_texts,
                }

                execute_sql(self._dbcurs, sql_uuid, params)
                r = self._dbcurs.fetchone()
                if r and r[0]:
                    self.all_uuid[self._class_id].append(r[0])

                execute_sql(self._dbcurs, sql_marker, params)
                self._dbcurs.fetchone()

        elif name in [u"node", u"way", u"relation", u"infos"]:
            if self.elem_mode == "info":
                self._elem[u"tag"] = self._elem_tags
                self._error_elements.append(self._elem)
            else:
                self._elem[u"create"] = self._fix_create
                self._elem[u"modify"] = self._fix_modify
                self._elem[u"delete"] = self._fix_delete
                self._fix.append(self._elem)

        elif name == u"class":
            self.all_uuid[self._class_id] = []

            # Commit class update on its own transaction. Avoid lock the class table and block other updates.
            dbconn = utils.get_dbconn()
            dbcurs = dbconn.cursor()
            sql  = u"INSERT INTO class (class, item, title, level, tags, detail, fix, trap, example, source, resource, timestamp) "
            sql += u"VALUES (%(class)s, %(item)s, %(title)s, %(level)s, %(tags)s, %(detail)s, %(fix)s, %(trap)s, %(example)s, %(source)s, %(resource)s, %(timestamp)s) "
            sql += u"ON CONFLICT (item, class) DO "
            sql += u"UPDATE SET title = %(title)s, level = %(level)s, tags = %(tags)s, detail = %(detail)s, fix = %(fix)s, trap = %(trap)s, example = %(example)s, source = %(source)s, resource = %(resource)s, timestamp = %(timestamp)s "
            sql += u"WHERE class.class = %(class)s AND class.item = %(item)s AND class.timestamp < %(timestamp)s AND "
            sql += u"      (class.title IS DISTINCT FROM %(title)s OR class.level IS DISTINCT FROM %(level)s OR class.tags IS DISTINCT FROM %(tags)s::varchar[] OR class.detail IS DISTINCT FROM %(detail)s OR class.fix IS DISTINCT FROM %(fix)s OR class.trap IS DISTINCT FROM %(trap)s OR class.example IS DISTINCT FROM %(example)s OR class.source IS DISTINCT FROM %(source)s OR class.resource IS DISTINCT FROM %(resource)s)"
            execute_sql(dbcurs, sql, {
                'class': self._class_id,
                'item': self._class_item[self._class_id],
                'title': self._class_title,
                'level': self._class_level,
                'tags': self._class_tags,
                'detail' : self._class_detail or None,
                'fix' : self._class_fix or None,
                'trap': self._class_trap or None,
                'example': self._class_example or None,
                'source': self._class_source or None,
                'resource': self._class_resource or None,
                'timestamp': utils.pg_escape(self.ts),
            })
            dbconn.commit()
            dbconn.close()

            sql  = u"INSERT INTO dynpoi_class (source, class, item, timestamp) "
            sql += u"VALUES (%(source)s, %(class)s, %(item)s, %(timestamp)s)"
            sql += u"ON CONFLICT (source, class) DO "
            sql += u"UPDATE SET item = %(item)s, timestamp = %(timestamp)s "
            sql += u"WHERE dynpoi_class.source = %(source)s AND dynpoi_class.class = %(class)s"
            execute_sql(self._dbcurs, sql, {
                'source': self._source_id,
                'class': self._class_id,
                'item': self._class_item[self._class_id],
                'timestamp':  utils.pg_escape(self.ts),
            })

        elif name == u"fixes":
            self.elem_mode = "info"
        elif name == u"fix" and self.element_stack[-1] == u"fixes":
            self._fixes.append(self._fix)

    def update_timestamp(self, attrs):
        self.ts = attrs.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.version = attrs.get("version", None)
        self.analyser_version = attrs.get("analyser_version", None)

        if not self._tstamp_updated:
            try:
                execute_sql(self._dbcurs, "INSERT INTO updates (source_id, timestamp, remote_url, remote_ip, version, analyser_version) VALUES(%s, %s, %s, %s, %s, %s);",
                                     (self._source_id, utils.pg_escape(self.ts),
                                      utils.pg_escape(self._source_url),
                                      utils.pg_escape(self._remote_ip),
                                      utils.pg_escape(self.version),
                                      utils.pg_escape(self.analyser_version)))
            except psycopg2.IntegrityError:
                self._dbconn.rollback()
                execute_sql(self._dbcurs, "SELECT count(*) FROM updates WHERE source_id = %s AND \"timestamp\" = %s",
                                     (self._source_id, utils.pg_escape(self.ts)))
                r = self._dbcurs.fetchone()
                if r["count"] == 1:
                    raise OsmoseUpdateAlreadyDone("source=%s and timestamp=%s are already present" % (self._source_id, utils.pg_escape(self.ts)))
                else:
                    raise

            execute_sql(self._dbcurs, "UPDATE updates_last SET timestamp=%s, version=%s, analyser_version=%s, remote_ip=%s WHERE source_id=%s;",
                                 (utils.pg_escape(self.ts),
                                  utils.pg_escape(self.version),
                                  utils.pg_escape(self.analyser_version),
                                  utils.pg_escape(self._remote_ip),
                                  self._source_id))
            if self._dbcurs.rowcount == 0:
                execute_sql(self._dbcurs, "INSERT INTO updates_last(source_id, timestamp, version, analyser_version, remote_ip) VALUES(%s, %s, %s, %s, %s);",
                                 (self._source_id,
                                  utils.pg_escape(self.ts),
                                  utils.pg_escape(self.version),
                                  utils.pg_escape(self.analyser_version),
                                  utils.pg_escape(self._remote_ip)))

            self._tstamp_updated = True

###########################################################################

def print_source(source):
    show(u"source #%s"%source["id"])
    for k in source:
        if k == "id":
            continue
        if type(source[k])== list:
            for e in source[k]:
                show(u"   %-10s = %s"%(k, e))
        else:
            show(u"   %-10s = %s"%(k, source[k]))

###########################################################################
import unittest

class Test(unittest.TestCase):

    def setUp(self):
        utils.pg_host = "localhost"
        utils.pg_base = "osmose_test"
        utils.pg_pass = "-osmose-"
        utils.db_string = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (utils.pg_host, utils.pg_port, utils.pg_base, utils.pg_user, utils.pg_pass)

        self.dbconn = utils.get_dbconn()
        self.dbcurs = self.dbconn.cursor()
        self.dbcurs.execute(open("tools/database/drop.sql", "r").read())
        self.dbcurs.execute(open("tools/database/schema.sql", "r").read())
        # Re-initialise search_path as cleared by schema.sql
        self.dbcurs.execute("SET search_path TO \"$user\", public;")
        self.dbcurs.execute("INSERT INTO sources (id, country, analyser) VALUES (%s, %s, %s);",
                       (1, "xx1", "yy1"))
        self.dbcurs.execute("INSERT INTO sources (id, country, analyser) VALUES (%s, %s, %s);",
                       (2, "xx2", "yy2"))
        self.dbcurs.execute("INSERT INTO sources_password (source_id, password) VALUES (%s, %s);",
                       (1, "xx1"))
        self.dbcurs.execute("INSERT INTO sources_password (source_id, password) VALUES (%s, %s);",
                       (2, "xx2"))
        self.dbconn.commit()

    def tearDown(self):
        self.dbconn.close()


    def check_num_marker(self, num):
        self.dbcurs.execute("SELECT count(*) FROM marker")
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

        with self.assertRaises(OsmoseUpdateAlreadyDone) as cm:
            update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

    def test_two_sources(self):
        self.check_num_marker(0)
        update(1, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

        update(2, "tests/Analyser_Osmosis_Broken_Highway_Level_Continuity-france_reunion-2014-06-11.xml.bz2")
        self.check_num_marker(50+99)

###########################################################################

if __name__ == "__main__":
    sources = utils.get_sources()
    if len(sys.argv) == 1:
        for k in sorted([int(x) for x in sources.keys()]):
            source = sources[str(k)]
            print_source(source)
    elif sys.argv[1] == "--help":
        show(u"usage: update.py <source number> <url>")
    else:
        update(utils.get_sources()[sys.argv[1]], sys.argv[2])
