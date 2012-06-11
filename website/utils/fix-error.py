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

###########################################################################
## database connection

import sys, os, cgi, tempfile, urllib
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils
from tools import OsmSax

import cgitb
cgitb.enable()

temp_path = "/tmp/osmose/"
remote_url = "http://api.openstreetmap.fr/api/0.6"

PgConn   = utils.get_dbconn()
PgCursor = PgConn.cursor()

form       = cgi.FieldStorage()
err_id     = form.getvalue("id", None)
fix_num    = form.getvalue("fix", 0)


try:
    err_id = int(err_id)
    fix_num = int(fix_num)
except:
    utils.print_header()
    print "Id '%s' is incorrect" % err_id
    sys.exit(0)

###########################################################################

data_type = { "N": "node",
              "W": "way",
              "R": "relation",
            }

class OsmSaxFixWriter(OsmSax.OsmSaxWriter):

    def __init__(self,
                 out, enc,
                 elem_type, elem_id,
                 tags_create, tags_modify, tags_delete):
        OsmSax.OsmSaxWriter.__init__(self, out, enc)

        self.elem_type = elem_type
        self.elem_id = elem_id
        self.tags_create = tags_create
        self.tags_modify = tags_modify
        self.tags_delete = tags_delete

    def fix_tags(self, data):
        for k in self.tags_delete:
            del data["tag"][k]
        for (k, v) in self.tags_create.items():
            data["tag"][k] = v
        for (k, v) in self.tags_modify.items():
            data["tag"][k] = v
        data["action"] = "modify"
        return data
 
    def NodeCreate(self, data):
        if self.elem_type == "N" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.NodeCreate(self, data)

    def WayCreate(self, data):
        if self.elem_type == "W" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.WayCreate(self, data)

    def RelationCreate(self, data):
        if self.elem_type == "R" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.RelationCreate(self, data)

###########################################################################

columns = [ "diff_index", "elem_data_type", "elem_id", "tags_create", "tags_modify", "tags_delete" ]

sql = "SELECT " + ", ".join(columns) + """
FROM marker_fix
WHERE marker_id = %s AND diff_index = %s
"""

PgCursor.execute(sql, (err_id, fix_num))
res = PgCursor.fetchall()
if res:
    print "Content-Type: text/xml; charset=utf-8"
    print
    print '<?xml version="1.0" encoding="UTF-8"?>'
    res = res[0]
    elem_file =  tempfile.mktemp(dir=temp_path, prefix="fix")
    elem_url = os.path.join(remote_url,
                            data_type[res["elem_data_type"]],
                            str(res["elem_id"])
                           )
    if res["elem_data_type"] == "W":
        elem_url = os.path.join(elem_url, "full")
    (filename, headers) = urllib.urlretrieve(elem_url, elem_file)
    osm_read = OsmSax.OsmSaxReader(elem_file)
    o = OsmSaxFixWriter(sys.stdout, "utf8",
                        res["elem_data_type"], res["elem_id"],
                        res["tags_create"], res["tags_modify"], res["tags_delete"])
    osm_read.CopyTo(o)
    os.remove(elem_file)

else:
    print "Status: 412 Precondition Failed"
    print "Content-Type: text/html; charset=utf-8"
    print
    print "No error found"
