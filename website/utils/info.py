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

form    = cgi.FieldStorage()
source  = form.getvalue("source", None)
class_  = form.getvalue("class", None)
item    = form.getvalue("item", None)
country = form.getvalue("country", None)
num_points = form.getvalue("points", None)

if source:
    source = int(source)
if class_:
    class_ = int(class_)
if item:
    item   = int(item)
if country and not re.match(r"^([a-z_]+)$", country):
    country = None
if num_points:
    num_points = int(num_points)
    if num_points <= 0:
        num_points = None
    elif num_points > 10000:
        num_points = 10000

if "info" in os.environ["SCRIPT_NAME"]:
    gen = "info"
    default_show_all = True
elif "false-positive" in os.environ["SCRIPT_NAME"]:
    gen = "false-positive"
    default_show_all = False
elif "done" in os.environ["SCRIPT_NAME"]:
    gen = "done"
    default_show_all = False
else:
    sys.exit(0)

show_all = form.getvalue("all", None)

if show_all == None:
    show_all = default_show_all
elif int(show_all) == 0:
    show_all = False
else:
    show_all = True


translate = utils.translator()
show = utils.show

###########################################################################
## page headers

utils.print_header()

query = os.environ["QUERY_STRING"]

show(u"<a href=\"info.py?%s\">%s</a>" % (query, _("Informations")))
show(u"<a href=\"done.py?%s\">%s</a>" % (query, _("Fixed")))
show(u"<a href=\"false-positive.py?%s\">%s</a>" % (query, _("False positives")))
show(u"<a href=\"graph.py?%s\">%s</a>" % (query, _("Graph")))
show(u"<a href=\"/map/?%s\">%s</a>" % (query, _("Map")))
show(u"<br><br>")

###########################################################################

show(u"<form method='get'>")

show(u"<select name='country'>")
show(u"<option value=''></option>")
sql = """
SELECT DISTINCT
  (string_to_array(comment,'-'))[array_upper(string_to_array(comment,'-'), 1)] AS country
FROM dynpoi_source
ORDER BY country;"""
PgCursor.execute(sql)
for res in PgCursor.fetchall():
    if country == res['country']:
        s = " selected='yes'"
    else:
        s = ""
    show(u"<option%s value='%s'>%s</option>" % (s, res['country'], res['country']))
show(u"</select>")

show(u"<select name='item'>")
show(u"<option value=''></option>")
sql = """
SELECT
  item,
  menu
FROM dynpoi_item
ORDER BY item;"""
PgCursor.execute(sql)
for res in PgCursor.fetchall():
    if item == res['item']:
        s = " selected='yes'"
    else:
        s = ""
    show(u"<option%s value='%s'>%s - %s</option>" % (s, res['item'], res['item'], translate.select(res['menu'])))
show(u"</select>")
show(u"<input type='submit' value='%s'/>" % _("Set"))

show(u"</form>")

###########################################################################

sql = """
SELECT
  dynpoi_class.source AS source,
  dynpoi_class.class AS class,
  dynpoi_class.item AS item,
  first(dynpoi_item.menu) AS menu,
  first(dynpoi_class.title) AS title,
  %s AS count,
  dynpoi_source.comment AS source_comment
FROM dynpoi_class
  LEFT JOIN dynpoi_item
    ON dynpoi_class.item = dynpoi_item.item
  LEFT JOIN dynpoi_source
    ON dynpoi_class.source = dynpoi_source.source
  %s %s
WHERE 1=1
  %s
GROUP BY
  dynpoi_class.source,
  dynpoi_class.class,
  dynpoi_class.item,
  dynpoi_source.comment
ORDER BY
  dynpoi_class.item,
  dynpoi_class.source
"""

if show_all:
    opt_left_join = "LEFT"
else:
    opt_left_join = ""

if gen == "info":
    opt_count = "count(marker.source)"
    opt_join = """JOIN marker
    ON dynpoi_class.source = marker.source
    AND dynpoi_class.class = marker.class
"""
elif gen == "false-positive":
    opt_count = "count(dynpoi_status.source)"
    opt_join = """JOIN dynpoi_status
    ON dynpoi_class.source = dynpoi_status.source
    AND dynpoi_class.class = dynpoi_status.class
    AND dynpoi_status.status = 'false'
"""
elif gen == "done":
    opt_count = "count(dynpoi_status.source)"
    opt_join = """JOIN dynpoi_status
    ON dynpoi_class.source = dynpoi_status.source
    AND dynpoi_class.class = dynpoi_status.class
    AND dynpoi_status.status = 'done'
"""

opt_where = ""

if source <> None:
    opt_where += " AND dynpoi_class.source = %d" % source
if class_ <> None:
    opt_where += " AND dynpoi_class.class = %d" % class_
if item <> None:
    opt_where += " AND dynpoi_class.item = %d" % item
if country <> None:
    opt_where += " AND dynpoi_source.comment LIKE '%%%s'" % ("-" + country)

if source == None and item == None and country == None:
    if show_all:
        opt_count = "-1"
        if gen == "info":
            opt_left_join = ""
            opt_join = ""

sql = sql % (opt_count, opt_left_join, opt_join, opt_where)

###########################################################################

show(u"<table class=\"sortable\" id =\"table_source\">")
show(u"<thead>")
show(u"<tr>")
show(u"  <th>#</th>")
show(u"  <th>%s</th>" % _("source"))
# TRANSLATORS: this should be replaced by a abbreviation for class
show(u"  <th title=\"class\">%s</th>" % _("class (abbreviation)"))
show(u"  <th></th>")
show(u"  <th class=\"sorttable_sorted\">#<span id=\"sorttable_sortfwdindtable_source\">&nbsp;▾</span></th>")
show(u"  <th>%s</th>" % _("item"))
show(u"  <th>%s</th>" % _("title"))
show(u"  <th>%s</th>" % _("count"))
show(u"</tr>")

show(u"</thead>")
PgCursor.execute(sql)
total = 0
odd = True
for res in PgCursor.fetchall():
    odd = not odd
    if odd:
        show(u"<tr class='odd'>")
    else:
        show(u"<tr class='even'>")

    show(u"<td><a href=\"?source=%d\">%d</a></td>" % ((res["source"],) * 2))
    cmt_split = res["source_comment"].split("-")
    analyse = "-".join(cmt_split[0:-1])
    country = cmt_split[-1]
    show(u"<td>%s-<a href=\"?country=%s\">%s</a></td>" % (analyse, country, country))
    show(u"<td><a href=\"?item=%d&amp;class=%d\">%d</a></td>" % (res["item"], res["class"], res["class"]))
    show(u"<td title=\"%s\"><img src=\"/map/markers/marker-l-%d.png\" alt=\"%s\"></td>" % ((res["item"],) * 3))
    show(u"<td><a href=\"?item=%d\">%d</a>" % ((res["item"],) * 2))
    show(u"</td>")
    if res["menu"]:
        show(u"<td>%s</td>" % translate.select(res["menu"]))
    else:
        show(u"<td></td>")
    show(u"<td>%s</td>" % translate.select(res["title"]))
    count = res["count"]
    if count == -1:
        count = "N/A"
    else:
        total += count
    show(u"<td><a href=\"?source=%d&amp;item=%d&amp;class=%d\">%s</a></td>" % (res["source"], res["item"], res["class"], count))
    show(u"</tr>")

if total > 0:
    show(u"<tfoot>")
    show(u"<tr>")
    show(u"  <th colspan=\"7\">Total</th>")
    show(u"  <th style=\"text-align: left\">%s</th>" % total)
    show(u"</tr>")
    show(u"</tfoot>")

show(u"</table>")
###########################################################################

if (total > 0 and total < 1000) or num_points:

    if gen == "info":
        opt_count = "count(marker.source)"
        opt_join = """JOIN marker
    ON dynpoi_class.source = marker.source
    AND dynpoi_class.class = marker.class
"""

    sql = """
SELECT
  %s
  dynpoi_class.source AS source,
  dynpoi_class.class AS class,
  dynpoi_class.item AS item,
  dynpoi_item.menu,
  dynpoi_class.title,
  subtitle,
  dynpoi_source.comment AS source_comment,
  subclass,
  lat,
  lon,
  elems AS elems,
  %s AS date
FROM dynpoi_class
  LEFT JOIN dynpoi_item
    ON dynpoi_class.item = dynpoi_item.item
  LEFT JOIN dynpoi_source
    ON dynpoi_class.source = dynpoi_source.source
  %s
WHERE 1=1 
  %s
ORDER BY
  %s
  dynpoi_class.item,
  dynpoi_class.source
"""

    if gen == "info":
        marker_id = "marker.id AS marker_id,"
        opt_date = "-1"
        opt_order = "subtitle->'en',"
    elif gen in ("false-positive", "done"):
        marker_id = ""
        opt_date = "date"
        opt_order = "dynpoi_status.date DESC,"
    if num_points:
        sql += "LIMIT %d" % num_points

    sql = sql % ((marker_id, ) + (opt_date, opt_join, opt_where, opt_order))

    show(u"<br>")

    show(u"<table class=\"sortable\">")
    show(u"<thead>")
    show(u"<tr>")
    show(u"  <th title=\"source\">%s</th>" % _("source"))
# TRANSLATORS: this should be replaced by a abbreviation for class
    show(u"  <th title=\"class\">%s</th>" % _("class (abbreviation)"))
# TRANSLATORS: this should be replaced by a abbreviation for subclass
    show(u"  <th title=\"subclass\">%s</th>" % _("subclass (abbreviation)"))
    show(u"  <th></th>")
    show(u"  <th>#</th>")
    show(u"  <th>%s</th>" % _("item"))
    if gen == "info":
        show(u"  <th title=\"%s\">E</th>" % _("information on error"))
    show(u"  <th title=\"%s\">%s</th>" % (_("position"), _("position (abbreviation)")))
    show(u"  <th>%s</th>" % _("elements (abbreviation)"))
    if opt_date != "-1":
        show(u"  <th>%s</th>" % _("subtitle"))
    else:
        show(u"  <th class=\"sorttable_sorted\">%s<span id=\"sorttable_sortfwdind\">&nbsp;▾</span></th>" % _("subtitle"))
    if opt_date != "-1":
        show(u"  <th class=\"sorttable_sorted\">%s<span id=\"sorttable_sortfwdind\">&nbsp;▾</span></th>" % _("date"))
    show(u"</tr>")
    show(u"</thead>")
    PgCursor.execute(sql)
    odd = True
    for res in PgCursor.fetchall():
        odd = not odd
        if odd:
            show(u"<tr class='odd'>")
        else:
            show(u"<tr class='even'>")
        show(u"<td title=\"%(cmt)s\"><a href=\"?source=%(src)d\">%(src)d</a> </td>" % {"cmt": res["source_comment"], "src": res["source"]})
        show(u"<td>%d</td>" % res["class"])
        show(u"<td>%d</td>" % res["subclass"])
        show(u"<td title=\"%(item)d\"><img src=\"/map/markers/marker-l-%(item)d.png\" alt=\"%(item)d\"></td>" % {"item": res["item"]})
        show(u"<td><a href=\"?item=%d\">%d</a> </td>"%(res["item"],res["item"]))
        if res["menu"]:
            show(u"<td title=\"%s\">%s</td>" % (translate.select(res["title"]),
                                                translate.select(res["menu"])))
        else:
            show(u"<td></td>")

        if gen == "info":
            show(u"<td title=\"erreur n°%s\"><a href='error.py?id=%s'>E</a></td>" % (res["marker_id"], res["marker_id"]))

        if res["lat"] and res["lon"]:
            lat = res["lat"] / 1000000.
            lon = res["lon"] / 1000000.
            show(u"<td><a href='/map/?zoom=13&amp;lat=%f&amp;lon=%f&amp;item=%d'>%.2f&nbsp;%.2f</a></td>" % (lat, lon, res["item"], lon, lat))
        else:
            show(u"<td></td>")

        printed_td = False
        if res["elems"]:
            elems = res["elems"].split("_")
            for e in elems:
                m = re.match(r"([a-z]+)([0-9]+)", e)
                if m:
                    if not printed_td:
                        show(u"<td sorttable_customkey=\"%02d%s\">" % (ord(m.group(1)[0]), m.group(2)))
                        printed_td = True
                    else:
                        show(u"&nbsp;")
                    cur_type = m.group(1)
                    sys.stdout.write("%s&nbsp;" % cur_type[0])
                    sys.stdout.write("<a target=\"_blank\" href=\"http://www.openstreetmap.org/browse/%s/%s\">%s</a>&nbsp;"%(m.group(1), m.group(2), m.group(2)))
                    if cur_type == "node":
                        full_str = ""
                    else:
                        full_str = "/full"
                    sys.stdout.write("&nbsp;<a title=\"josm\" href=\"http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/%s/%s%s\" target=\"hiddenIframe\">(j)</a>" % (m.group(1), m.group(2), full_str))

        if not printed_td:
            minlat = lat - 0.002
            maxlat = lat + 0.002
            minlon = lon - 0.002
            maxlon = lon + 0.002
            show(u"<td>")
            show(u"<a href=\"http://localhost:8111/load_and_zoom?left=%f&bottom=%f&right=%f&top=%f"%(minlon,minlat,maxlon,maxlat) + "\">josm</a>")

        show(u"</td>")
        if res["subtitle"]:
            show(u"<td>%s</td>" % translate.select(res["subtitle"]))
        elif res["title"]:
            show(u"<td>%s</td>" % translate.select(res["title"]))
        else:
            show(u"<td></td>")
        if opt_date != "-1":
            date = str(res["date"])
            show(u"<td>%s&nbsp;%s</td>" % (date[:10], date[11:16]))
        show(u"</tr>")
    show(u"</table>")

    if num_points and total > num_points:
        import urlparse, urllib
        query_dict = urlparse.parse_qs(query)
        query_dict["points"] = 5 * num_points
        show(u"<br>")
        show(u"<a href='?%s'>Afficher plus d'erreurs</a>" % urllib.urlencode(query_dict, True))

else:
    show(u"<br>")
    show(u"<a href='?%s'>Afficher quelques erreurs</a>" % (query + "&amp;points=100"))

###########################################################################
utils.print_tail()
