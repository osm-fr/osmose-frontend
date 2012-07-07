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

translate = utils.translator()
show = utils.show

if username=="":
    utils.print_header(_("OsmOse - statistics for user"))
    show(u"<form method='GET' action=''>")
    show(u"<label for='username'>%s</label>" % _("Username:"))
    show(u"<input type='text' name='username' id='username'>")
    show(u"<input type='submit'>")
    show(u"</form>")
    sys.exit(0)

###########################################################################
## page headers

utils.print_header(_("OsmOse - statistics for user %s") % username)

###########################################################################


sql = """--
SELECT m.id, m.class, m.subtitle, m.lat, m.lon, m.source, m.item,
       c.title, c.level
FROM marker m
JOIN dynpoi_class c ON m.class = c.class AND
                       m.source = c.source
JOIN dynpoi_item
  ON m.item = dynpoi_item.item
WHERE id IN (SELECT marker_id FROM marker_elem WHERE username=%s)
ORDER BY m.class
LIMIT 500;"""

PgCursor.execute(sql, (username.encode('utf-8'), ))
results = PgCursor.fetchall()
count = len(results)

show(u"<h1>%s</h1>" % (_("User statistics for %s") % username))
show(u"<p>")
show(_("This page shows errors on elements that were last modified by '%s'. This doesn't means that this user is responsible for all these errors.") % username)
show(u"</p>")
show(u"<p>")
if count < 500:
    show(_("Number of found errors: %d") % count)
else:
    show(_("Number of found errors: more than %d") % count)
show(u"</p>")

show(u"<table class='sortable byuser'>\n")
show(u"  <tr>\n")
show(u"    <th>%s</th>\n" % _("Item"))
show(u"    <th>%s<span id=\"sorttable_sortfwdind\">&nbsp;▾</span></th>\n" % _("Class"))
show(u"    <th>%s</th>\n" % _("Level"))
show(u"    <th>%s</th>\n" % _("Title"))
show(u"    <th>%s</th>\n" % _("Error"))
show(u"    <th>%s</th>\n" % _("Latitude"))
show(u"    <th>%s</th>\n" % _("Longitude"))
show(u"    <th></th>\n")
show(u"  </tr>\n")

for res in results:
    show(u"  <tr>\n")
    show(u"    <td>" + str(res["item"]) + "</td>\n")
    show(u"    <td>" + str(res["class"]) + "</td>\n")
    show(u"    <td>" + str(res["level"]) + "</td>\n")
    show(u"    <td>" + translate.select(res["title"]) + "</td>\n")
    show(u"    <td>\n")
    if res["subtitle"] is None:
        pass
    else:
        show(translate.select(res["subtitle"]))
    show(u"    </td>\n")
    lat = str(float(res["lat"])/1000000)
    lon = str(float(res["lon"])/1000000)
    cl = res["class"]
    source = res["source"]
    item = res["item"]
    level = res["level"]
#    url = "/map/?zoom=16&amp;lat=%s&amp;lon=%s&amp;source=%s" % (lat, lon, source)
    url = "/map/?zoom=16&amp;lat=%s&amp;lon=%s&amp;item=%s&amp;level=%d" % (lat, lon, item, level)
    show(u"    <td>" + lat + "</td>\n")
    show(u"    <td>" + lon + "</td>\n")
    show(u"    <td><a href='" + url + "'>%s</a></td>\n" % _("map"))
    show(u"  </tr>\n")

show(u"</table>\n")

###########################################################################
utils.print_tail()
