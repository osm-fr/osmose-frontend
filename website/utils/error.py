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

import sys, os, time, cgi, re
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

import cgitb
cgitb.enable()

PgConn   = utils.get_dbconn()
PgCursor = PgConn.cursor()

form       = cgi.FieldStorage()
err_id     = form.getvalue("id", None)
out_format = form.getvalue("format", "html")

translate = utils.translator()
show = utils.show
N_ = utils.N_

try:
    err_id = int(err_id)
except:
    utils.print_header()
    show(u"Id '%s' is incorrect" % err_id)
    sys.exit(0)

if out_format not in ("html", "json", "xml"):
    utils.print_header()
    show(u"Format '%s' not supported" % out_format)
    sys.exit(0)

###########################################################################
## page headers

if out_format == "html":
    utils.print_header(title=N_("OsmOse - information on error %d") % err_id)
elif out_format == "json":
    show(u"Content-Type: application/javascript; charset=utf-8")
    print
elif out_format == "xml":
    show(u"Content-Type: text/xml; charset=utf-8")
    print
    from tools import OsmSax
    outxml = OsmSax.OsmSaxWriter(sys.stdout, "UTF-8")
    print '<?xml version="1.0" encoding="UTF-8"?>'
    outxml.startElement("error", { "id": str(err_id) })

###########################################################################

data_type = { "N": "node",
              "W": "way",
              "R": "relation",
            }

def show_html_results(columns, res):

    show(u"<table class=\"sortable\" id =\"table_marker\">")
    show(u"<thead>")
    show(u"<tr>")
    show(u"  <th>%s</th>" % _("key"))
    show(u"  <th>%s</th>" % _("value"))
    show(u"</tr>")
    show(u"</thead>")

    odd = True
    for c in columns:
        c = c.split(".")[-1]
        odd = not odd
        if odd:
            show(u"<tr class='odd'>")
        else:
            show(u"<tr class='even'>")

        show(u"<td>%s</td>" % c)
        show(u"<td>")
        if type(res[c]) is dict:
            show(u"<table>")
            for (k, v) in res[c].items():
                show(u"<tr><td>%s</td><td>%s</td></tr>" % (k, v))
            show(u"</table>")
        else:
            show(unicode(res[c]))
        show(u"</td>")
        show(u"</tr>")

    show(u"</table>")


###########################################################################

if out_format == "html":
    show(u"<h2>%s</h2>" % _("Marker"))
elif out_format == "json":
    pass
elif out_format == "xml":
    outxml.startElement("marker")

columns = [ "marker.source", "marker.class", "subclass", "lat", "lon", "elems", "marker.item", "subtitle", "title" ]

sql = "SELECT " + ", ".join(columns) + """
FROM marker
LEFT JOIN dynpoi_class on marker.class = dynpoi_class.class AND marker.source = dynpoi_class.source
WHERE id = %s
"""

PgCursor.execute(sql, (err_id, ))
for res in PgCursor.fetchall():
    if out_format == "html":
        show_html_results(columns, res)

if out_format == "xml":
    outxml.endElement("marker")

###########################################################################

if out_format == "html":
    show(u"<h2>%s</h2>" % _("Elements"))
elif out_format == "json":
    pass
elif out_format == "xml":
    outxml.startElement("elems")

columns = [ "elem_index", "data_type", "id", "tags", "username" ]

sql = "SELECT " + ", ".join(columns) + """
FROM marker_elem
WHERE marker_id = %s
ORDER BY elem_index
"""

PgCursor.execute(sql, (err_id, ))
for res in PgCursor.fetchall():
    if out_format == "html":
        show_html_results(columns, res)

if out_format == "xml":
    outxml.endElement("elems")

###########################################################################

if out_format == "html":
    show(u"<h2>%s</h2>" % _("Fixes"))
elif out_format == "json":
    pass
elif out_format == "xml":
    outxml.startElement("fixes")

columns = [ "diff_index", "elem_data_type", "elem_id", "tags_create", "tags_modify", "tags_delete" ]

sql = "SELECT " + ", ".join(columns) + """
FROM marker_fix
WHERE marker_id = %s
ORDER BY diff_index
"""

PgCursor.execute(sql, (err_id, ))
for res in PgCursor.fetchall():
    if out_format == "html":
        show_html_results(columns, res)

    elif out_format == "xml":
        outxml.startElement("fix")
        outxml.startElement(data_type[res["elem_data_type"]], {"id": str(res["elem_id"])})
        for (k, v) in res["tags_create"].items():
            outxml.Element("tag", { "action": "create", "k": k, "v": v})
        for (k, v) in res["tags_modify"].items():
            outxml.Element("tag", { "action": "modify", "k": k, "v": v})
        for k in res["tags_delete"]:
            outxml.Element("tag", { "action": "delete", "k": k})
        outxml.endElement(data_type[res["elem_data_type"]])
        outxml.endElement("fix")

if out_format == "xml":
    outxml.endElement("fixes")

###########################################################################
if out_format == "html":
    utils.print_tail()
elif out_format == "json":
    pass
elif out_format == "xml":
    outxml.endElement("error")
