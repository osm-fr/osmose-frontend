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

import sys, os, time, urllib, tempfile, commands
import psycopg2
import utils
import socket
from xml.sax import make_parser, handler

show = utils.show

###########################################################################
## logger

class printlogger:
    def log(self, text):
        print text

###########################################################################
## updater

class OsmoseUpdateAlreadyDone(Exception):
    pass

num_sql_run = 0
prev_sql = ""

def execute_sql(dbcurs, sql, args = None):
    global prev_sql, num_sql_run
    try:
        if args == None:
            dbcurs.execute(sql)
        else:
            dbcurs.execute(sql, args)
    except:
        print sql, args
        raise
    num_sql_run += 1
    if num_sql_run % 10000 == 0:
        print ".",
        sys.stdout.flush()

def update(source, url, logger = printlogger(), remote_ip=""):

    source_id = int(source["id"])

    ## open connections
    dbconn = utils.get_dbconn()
    dbcurs = dbconn.cursor()

    ## xml parser
    parser = make_parser()
    parser.setContentHandler(update_parser(source_id, source, url, remote_ip, dbconn, dbcurs))

    ## download the file if needed
    if url.startswith("http://"):
        socket.setdefaulttimeout(180)


        tmp_path = "/tmp/osmose/"
        if not os.path.exists(tmp_path):
            os.makedirs(tmp_path)
        fname =  tempfile.mktemp(dir=tmp_path, prefix="update")
        urllib.urlretrieve(url, fname)
        #mysock = urllib.urlopen(source["url"])
        #open(fname,'w').write(mysock.read())
        istemp = True
    else:
        fname = url
        istemp = False

    ## open the file
    if url.endswith(".bz2"):
        import bz2
        f = bz2.BZ2File(fname)
    elif url.endswith(".gz"):
        import gzip
        f = gzip.open(fname)
    else:
        f = open(fname)

    ## parse the file
    parser.parse(f)

    ## update subtitle from new errors
    execute_sql(dbcurs, """SELECT * FROM marker
                      WHERE (source,class,subclass,elems) IN (SELECT source,class,subclass,elems FROM dynpoi_status WHERE source = %s AND elems != '')""",
                   (source_id, ))
    for res in dbcurs.fetchall():
        execute_sql(dbcurs, """UPDATE dynpoi_status SET subtitle = %s,
                                                        lat = %s, lon = %s
                          WHERE source = %s AND class = %s AND subclass = %s AND elems = %s""",
                       (res["subtitle"], res["lat"], res["lon"],
                        res["source"], res["class"], res["subclass"], res["elems"]))

    execute_sql(dbcurs, """SELECT * FROM marker
                      WHERE (source,class,subclass,lat,lon) IN (SELECT source,class,subclass,lat,lon FROM dynpoi_status WHERE source = %s AND elems = '')""",
                   (source_id, ))
    for res in dbcurs.fetchall():
        execute_sql(dbcurs, """UPDATE dynpoi_status SET subtitle = %s
                          WHERE source = %s AND class = %s AND subclass = %s AND lat = %s AND lon = %s""",
                       (res["subtitle"],
                        res["source"], res["class"], res["subclass"], res["lat"], res["lon"]))


    ## remove false positive no longer present
#    execute_sql(dbcurs, """DELETE FROM dynpoi_status
#                      WHERE (source,class,subclass,elems) NOT IN (SELECT source,class,subclass,elems FROM marker WHERE source = %s) AND
#                            source = %s AND
#                            date < now()-interval '7 day'""",
#                   (source_id, source_id, ))

    execute_sql(dbcurs, """DELETE FROM marker
                      WHERE (source,class,subclass,elems) IN (SELECT source,class,subclass,elems FROM dynpoi_status WHERE source = %s AND elems != '')""",
                   (source_id, ))

    execute_sql(dbcurs, """DELETE FROM marker
                      WHERE (source,class,subclass,lat,lon) IN (SELECT source,class,subclass,lat,lon FROM dynpoi_status WHERE source = %s AND elems = '')""",
                   (source_id, ))

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
    if istemp:
        os.remove(fname)

class update_parser(handler.ContentHandler):

    def __init__(self, source_id, source_data, source_url, remote_ip, dbconn, dbcurs):
        self._source_id        = source_id
        self._source_data      = source_data
        self._source_url       = source_url
        self._remote_ip        = remote_ip
        self._dbconn           = dbconn
        self._dbcurs           = dbcurs
        self._class_texts      = {}
        self._class_item       = {}
        self._tstamp_updated   = False

    def setDocumentLocator(self, locator):
        self.locator = locator

    def startElement(self, name, attrs):
        if name == u"analyser":
            self.mode = "analyser"
            self.update_timestamp(attrs)

        elif name == u"analyserChange":
            self.mode = "analyserChange"
            self.update_timestamp(attrs)

        elif name == u"error":
            self._class_id        = int(attrs["class"])
            self._class_sub       = int(attrs.get("subclass", u"0"))%2147483647
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
            self._class_texts = {}
            if "tag" in attrs:
                self._class_tags = attrs["tag"].split(",")
            else:
                self._class_tags = []

        elif name == u"classtext":
            self._class_texts[attrs["lang"]] = attrs["title"]
        elif name == u"delete":
            # used by files generated with an .osc file
            execute_sql(self._dbcurs, """DELETE FROM marker
                                    WHERE source = %s AND id IN
                                          (SELECT marker_id FROM marker_elem
                                           WHERE data_type = %s AND id = %s)""",
                                 (self._source_id, attrs["type"][0].upper(), attrs["id"]))

        elif name == u"fixes":
            self.elem_mode = "fix"
        elif name == u"fix":
            self._fix = []
            self._fix_create = {}
            self._fix_modify = {}
            self._fix_delete = []

    def endElement(self, name):
        if name == u"error":
            ## build all_elem
            all_elem   = u""
            for e in self._error_elements:
                all_elem  += e[u"type"] + e[u"id"] + "_"
            all_elem  = all_elem.rstrip("_")

            ## sql template
            sql_marker = u"INSERT INTO marker (source, class, subclass, item, lat, lon, elems, subtitle) VALUES (" + "%s," * 7 + "%s) RETURNING id;"

            ## add data at all location
            if len(self._error_locations) == 0:
                print "No location on error found on line %d" % self.locator.getLineNumber()
                return

            cpt = 0
            for location in self._error_locations:
                cpt += 1
                                
                lat = float(location["lat"])
                lon = float(location["lon"])
                
                execute_sql(self._dbcurs, sql_marker,
                            (self._source_id, self._class_id, self._class_sub,
                             self._class_item[self._class_id],
                             lat, lon,
                             utils.pg_escape(all_elem),
                             self._error_texts,
                             ))
                marker_id = self._dbcurs.fetchone()[0]

            ## add all elements
            sql_elem = u"INSERT INTO marker_elem (marker_id, elem_index, data_type, id, tags, username) VALUES (" + "%s, " * 5 + "%s)"
            num = 0
            for elem in self._error_elements:
                if elem["type"] in ("node", "way", "relation"):
                    execute_sql(self._dbcurs, sql_elem,
                                (marker_id, num, elem["type"][0].upper(), int(elem["id"]),
                                 elem["tag"], elem["user"]))
                    num += 1
                if elem["type"] in ("infos"):
                    execute_sql(self._dbcurs, sql_elem,
                                (marker_id, num, elem["type"][0].upper(), 0,
                                 elem["tag"], elem["user"]))
                    num += 1

            ## add quickfixes
            sql_fix = u"INSERT INTO marker_fix (marker_id, diff_index, elem_data_type, elem_id, tags_create, tags_modify, tags_delete) VALUES (" + "%s, " * 6 + "%s)"
            num = 0
            for fix in self._fixes:
                for elem in fix:
                    if elem["type"] in ("node", "way", "relation"):
                        execute_sql(self._dbcurs, sql_fix,
                                    (marker_id, num, elem["type"][0].upper(), int(elem["id"]),
                                     elem["tags_create"], elem["tags_modify"], elem["tags_delete"]))
                num += 1


        elif name in [u"node", u"way", u"relation", u"infos"]:
            if self.elem_mode == "info":
                self._elem[u"tag"] = self._elem_tags
                self._error_elements.append(self._elem)
            else:
                self._elem[u"tags_create"] = self._fix_create
                self._elem[u"tags_modify"] = self._fix_modify
                self._elem[u"tags_delete"] = self._fix_delete
                self._fix.append(self._elem)

        elif name == u"class":
            keys = ["source", "class", "item", "title", "level", "tags", "timestamp"]
            vals = [self._source_id, self._class_id,
                    self._class_item[self._class_id],
                    self._class_texts,
                    self._class_level,
                    self._class_tags,
                    utils.pg_escape(self.ts),
                   ]
            if self.mode == "analyser":
                execute_sql(self._dbcurs, "DELETE FROM marker WHERE source = %s AND class = %s;",
                                     (self._source_id, self._class_id))

                execute_sql(self._dbcurs, "DELETE FROM dynpoi_class WHERE source = %s AND class = %s",
                                     (self._source_id, self._class_id))
                sql  = u"INSERT INTO dynpoi_class (" + u','.join(keys) + u") "
                sql += u"VALUES (" + (u','.join(["%s"] * len(keys))) + u");"
                execute_sql(self._dbcurs, sql, vals)

            else:
                sql  = u"UPDATE dynpoi_class SET " + (u' = %s, '.join(keys)) + u" = %s "
                sql += u"WHERE source = %s AND class = %s;"
                ch_vals = vals + [self._source_id, self._class_id]
                execute_sql(self._dbcurs, sql, ch_vals)

                if self._dbcurs.rowcount == 0:
                    sql  = u"INSERT INTO dynpoi_class (" + u','.join(keys) + u") "
                    sql += u"VALUES (" + (u','.join(["%s"] * len(keys))) + u");"
                    execute_sql(self._dbcurs, sql, vals)

        elif name == u"fixes":
            self.elem_mode = "info"
        elif name == u"fix":
            self._fixes.append(self._fix)

    def update_timestamp(self, attrs):
        self.ts = attrs.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
        self.version = attrs.get("version", None)

        if not self._tstamp_updated:
            try:
                execute_sql(self._dbcurs, "INSERT INTO dynpoi_update (source, timestamp, remote_url, remote_ip, version) VALUES(%s, %s, %s, %s, %s);",
                                     (self._source_id, utils.pg_escape(self.ts),
                                      utils.pg_escape(self._source_url),
                                      utils.pg_escape(self._remote_ip),
                                      utils.pg_escape(self.version)))
            except psycopg2.IntegrityError:
                self._dbconn.rollback()
                execute_sql(self._dbcurs, "SELECT count(*) FROM dynpoi_update WHERE source = %s AND \"timestamp\" = %s",
                                     (self._source_id, utils.pg_escape(self.ts)))
                r = self._dbcurs.fetchone()
                if r["count"] == 1:
                    raise OsmoseUpdateAlreadyDone, "source=%s and timestamp=%s are already present" % (self._source_id, utils.pg_escape(self.ts))
                else:
                    raise

            execute_sql(self._dbcurs, "UPDATE dynpoi_update_last SET timestamp=%s, version=%s, remote_ip=%s WHERE source=%s;",
                                 (utils.pg_escape(self.ts),
                                  utils.pg_escape(self.version),
                                  utils.pg_escape(self._remote_ip),
                                  self._source_id))
            if self._dbcurs.rowcount == 0:
                execute_sql(self._dbcurs, "INSERT INTO dynpoi_update_last VALUES(%s, %s, %s, %s);",
                                 (self._source_id, utils.pg_escape(self.ts),
                                  utils.pg_escape(self.version),
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
        utils.pg_base = "osmose_test"
        utils.pg_pass = "-osmose-"

        self.dbconn = utils.get_dbconn()
        self.dbcurs = self.dbconn.cursor()
        self.dbcurs.execute(open("tools/database/drop.sql", "r").read())
        self.dbcurs.execute(open("tools/database/schema.sql", "r").read())
        self.dbcurs.execute("INSERT INTO source (id, country, analyser) VALUES (%s, %s, %s);",
                       (1, "xx1", "yy1"))
        self.dbcurs.execute("INSERT INTO source (id, country, analyser) VALUES (%s, %s, %s);",
                       (2, "xx2", "yy2"))
        self.dbcurs.execute("INSERT INTO source_password (source_id, password) VALUES (%s, %s);",
                       (1, "xx1"))
        self.dbcurs.execute("INSERT INTO source_password (source_id, password) VALUES (%s, %s);",
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
        update({"id": 1}, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

    def test_update(self):
        self.check_num_marker(0)
        update({"id": 1}, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-05-20.xml.bz2")
        self.check_num_marker(48)

        update({"id": 1}, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)


    def test_duplicate_update(self):
        self.check_num_marker(0)
        update({"id": 1}, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

        with self.assertRaises(OsmoseUpdateAlreadyDone) as cm:
            update({"id": 1}, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

    def test_two_sources(self):
        self.check_num_marker(0)
        update({"id": 1}, "tests/Analyser_Osmosis_Soundex-france_alsace-2014-06-17.xml.bz2")
        self.check_num_marker(50)

        update({"id": 2}, "tests/Analyser_Osmosis_Broken_Highway_Level_Continuity-france_reunion-2014-06-11.xml.bz2")
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
