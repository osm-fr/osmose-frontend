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

from bottle import route, request, template, response, abort
import StringIO, os, tempfile, urllib2

from tools import osmose_common


@route('/error/<err_id:int>')
@route('/error/<err_id:int>.<format:ext>')
def display(db, err_id=None, format=None):
    if not err_id:
        abort(401, "Id is incorect.")

    columns_marker = [ "marker.source", "marker.class", "subclass", "lat", "lon", "elems", "marker.item", "subtitle", "title", "level", "timestamp" ]
    sql = "SELECT " + ", ".join(columns_marker) + """
FROM marker
LEFT JOIN dynpoi_class on marker.class = dynpoi_class.class AND marker.source = dynpoi_class.source
LEFT JOIN dynpoi_update_last on marker.source = dynpoi_update_last.source
WHERE id = %s
"""
    db.execute(sql, (err_id, ))
    marker = db.fetchall()

    columns_elements = [ "elem_index", "data_type", "id", "tags", "username" ]
    sql = "SELECT " + ", ".join(columns_elements) + """
FROM marker_elem
WHERE marker_id = %s
ORDER BY elem_index
"""
    db.execute(sql, (err_id, ))
    elements = db.fetchall()

    columns_fix = [ "diff_index", "elem_data_type", "elem_id", "tags_create", "tags_modify", "tags_delete" ]
    sql = "SELECT " + ", ".join(columns_fix) + """
FROM marker_fix
WHERE marker_id = %s
ORDER BY diff_index
"""
    db.execute(sql, (err_id, ))
    fix = db.fetchall()

    if not format or format == 'html':
        return template('error/index', err_id=err_id,
            marker=marker, columns_marker=columns_marker,
            elements=elements, columns_elements=columns_elements,
            fix=fix, columns_fix=columns_fix)
    elif format == 'json':
        return {'err_id':err_id, 'marker':marker, 'elements':elements, 'fix':fix}
    elif format == 'xml':
        pass


@route('/error/<err_id:int>/<status:re:(done|false)>')
def status(db, err_id=None, status=None):
    if not err_id:
        abort(401, "Id is incorect.")

    if osmose_common.remove_bug(err_id, status) == 0:
        return "OK"
    else:
        return "FAIL"


@route('/error/<err_id:int>/fix')
@route('/error/<err_id:int>/fix/<fix_num:int>')
def fix(db, err_id=None, fix_num=0):
    if not err_id:
        abort(401, "Id is incorect.")

    remote_url = "http://api.openstreetmap.fr/api/0.6"

    data_type = {"N": "node", "W": "way", "R": "relation"}

    columns = [ "diff_index", "elem_data_type", "elem_id", "tags_create", "tags_modify", "tags_delete" ]
    sql = "SELECT " + ", ".join(columns) + """
FROM marker_fix
WHERE marker_id = %s AND diff_index = %s
"""

    db.execute(sql, (err_id, fix_num))
    res = db.fetchone()
    if res:
        response.content_type = 'text/xml; charset=utf-8'
        if res["elem_id"] > 0:
            elem_url = os.path.join(remote_url,
                                    data_type[res["elem_data_type"]],
                                    str(res["elem_id"])
                                   )
            if res["elem_data_type"] == "W":
                elem_url = os.path.join(elem_url, "full")
            elem_io = urllib2.urlopen(elem_url)
            osm_read = OsmSax.OsmSaxReader(elem_io)
            out = StringIO.StringIO()
            o = OsmSaxFixWriter(out, "UTF-8",
                                res["elem_data_type"], res["elem_id"],
                                res["tags_create"], res["tags_modify"], res["tags_delete"])
            o.startDocument()
            osm_read.CopyTo(o)

            return out.getvalue()

        else:
            # create new object
            data = {}
            data["id"] = -1
            data["tag"] = {}
            for (k, v) in res["tags_create"].iteritems():
                data["tag"][k] = v
            sql = "SELECT lat, lon FROM marker WHERE id = %s"
            db.execute(sql, (err_id, ))
            res2 = db.fetchone()
            data["lat"] = res2["lat"] / 1000000.
            data["lon"] = res2["lon"] / 1000000.

            if res["elem_data_type"] == 'N':
                return OsmSax.NodeToXml(data, full=True)
            elif res["elem_data_type"] == 'W':
                return OsmSax.WayToXml(data, full=True)
            elif res["elem_data_type"] == 'R':
                return OsmSax.RelationToXml(data, full=True)

    else:
        abort(412, "Precondition Failed")
        #print "No error found"



from tools import OsmSax

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

