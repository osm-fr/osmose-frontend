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


try:
    err_id = int(err_id)
except:
    utils.print_header()
    print "Id '%s' is incorrect" % err_id
    sys.exit(0)

if out_format not in ("html", "json", "xml"):
    utils.print_header()
    print "Format '%s' not supported" % out_format
    sys.exit(0)

###########################################################################
## page headers

if out_format == "html":
    utils.print_header()
elif out_format == "json":
    print "Content-Type: application/javascript; charset=utf-8"
    print
elif out_format == "xml":
    print "Content-Type: text/xml; charset=utf-8"
    print
    print '<?xml version="1.0" encoding="UTF-8"?>'
    print '<error id="%d">' % err_id

###########################################################################


def show_results(columns, res):

    print "<table class=\"sortable\" id =\"table_marker\">"
    print "<thead>"
    print "<tr>"
    print "  <th>clé</th>"
    print "  <th>valeur</th>"
    print "</tr>"
    print "</thead>"

    odd = True
    for c in columns:
        odd = not odd
        if odd:
            print "<tr class='odd'>"
        else:
            print "<tr class='even'>"

        print "<td>%s</td>" % c
        print "<td>"
        if type(res[c]) is dict:
            print "<table>"
            for (k, v) in res[c].items():
                print "<tr><td>%s</td><td>%s</td></tr>" % (k, v)
            print "</table>"
        else:
            print res[c]
        print "</td>"
        print "</tr>"

    print "</table>"


###########################################################################

if out_format == "html":
    print "<h2>Marqueur</h2>"
elif out_format == "json":
    pass
elif out_format == "xml":
    print "<marker>"

columns = [ "source", "class", "subclass", "lat", "lon", "elems", "item", "subtitle" ]

sql = "SELECT " + ", ".join(columns) + """
FROM marker
WHERE id = %s
"""

PgCursor.execute(sql, (err_id, ))
for res in PgCursor.fetchall():
    show_results(columns, res)

if out_format == "xml":
    print "</marker>"

###########################################################################

if out_format == "html":
    print "<h2>Éléments</h2>"
elif out_format == "json":
    pass
elif out_format == "xml":
    print "<elems>"

columns = [ "elem_index", "data_type", "id", "tags", "username" ]

sql = "SELECT " + ", ".join(columns) + """
FROM marker_elem
WHERE marker_id = %s
ORDER BY elem_index
"""

PgCursor.execute(sql, (err_id, ))
for res in PgCursor.fetchall():
    show_results(columns, res)

if out_format == "xml":
    print "</elems>"

###########################################################################

if out_format == "html":
    print "<h2>Corrections</h2>"
elif out_format == "json":
    pass
elif out_format == "xml":
    print "<fixes>"

columns = [ "diff_index", "elem_data_type", "elem_id", "tags_create", "tags_modify", "tags_delete" ]

sql = "SELECT " + ", ".join(columns) + """
FROM marker_fix
WHERE marker_id = %s
ORDER BY diff_index
"""

PgCursor.execute(sql, (err_id, ))
for res in PgCursor.fetchall():
    show_results(columns, res)

if out_format == "xml":
    print "</fixes>"

###########################################################################
if out_format == "html":
    utils.print_tail()
elif out_format == "json":
    pass
elif out_format == "xml":
    print "</error>"
