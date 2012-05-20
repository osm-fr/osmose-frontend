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

import sys, os, cgi
osmose_root = os.environ["OSMOSE_ROOT"]
sys.path.append(osmose_root)
from tools import utils

PgConn    = utils.get_dbconn()
PgCursor  = PgConn.cursor()
form      = cgi.FieldStorage()
username  = utils.pg_escape(unicode(form.getvalue("username", ""), "utf-8"))

if username=="":
    print "Content-Type: text/html; charset=utf-8"
    print
    print open("../index.html").read()
    sys.exit(0)

###########################################################################
## page headers

translate = utils.translator()
utils.print_header(translate)

###########################################################################


sql = """--
SELECT m.id, m.class, m.subtitle, m.lat, m.lon, m.source, m.item,
       c.title
FROM marker m
JOIN dynpoi_class c ON m.class = c.class AND
                       m.source = c.source
WHERE id IN (SELECT marker_id FROM marker_elem WHERE username=%s)
ORDER BY m.class
LIMIT 500;"""

print "<table class='byuser'>\n"
print "  <tr>\n"
print "    <th>Item</th>\n"
print "    <th>Class</th>\n"
print "    <th>Titre</th>\n"
print "    <th>Erreur</th>\n"
print "    <th>Latitude</th>\n"
print "    <th>Longitude</th>\n"
print "  </tr>\n"

PgCursor.execute(sql, (username.encode('utf-8'), ))

for res in PgCursor.fetchall():
    print "  <tr>\n"
    print "    <td>" + str(res["item"]) + "</td>\n"
    print "    <td>" + str(res["class"]) + "</td>\n"
    print "    <td>" + translate.select(res["title"]) + "</td>\n"
    print "    <td>\n"
    if res["subtitle"] is None:
        pass
    else:
        print translate.select(res["subtitle"])
    print "    </td>\n"
    lat = str(float(res["lat"])/1000000)
    lon = str(float(res["lon"])/1000000)
    cl = res["class"]
    source = res["source"]
    item = res["item"]
    url = "/map/cgi-bin/index.py?zoom=16&lat=%s&lon=%s&source=%s" % (lat, lon, source)
    url = "/map/cgi-bin/index.py?zoom=16&lat=%s&lon=%s&item=%s" % (lat, lon, item)
    print "    <td>" + lat + "</td>\n"
    print "    <td>" + lon + "</td>\n"
    print "    <td><a href='" + url + "'>carte</a></td>\n"
    print "  </tr>\n"

print "</table>\n"

###########################################################################
utils.print_tail()
