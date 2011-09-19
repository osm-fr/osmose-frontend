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
item    = form.getvalue("item", None)
country = form.getvalue("country", None)

if source:
    source = int(source)
if item:
    item   = int(item)
if country and not re.match(r"^([a-z_]+)$", country):
    country = None

if "info" in os.environ["SCRIPT_NAME"]:
    gen = "info"
    default_show_all = True
elif "false-positive" in os.environ["SCRIPT_NAME"]:
    gen = "false-positive"
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

###########################################################################
## page headers

utils.print_header()

query = os.environ["QUERY_STRING"]

print "<a href=\"info.py?%s\">Informations</a> <a href=\"false-positive.py?%s\">Faux positifs</a>" % ((query,) * 2)
print "<a href=\"graph.py?%s\">Graphe</a> <a href=\"/map/?%s\">Carte</a>" % ((query,) * 2)
print "<br><br>"

###########################################################################

sql = """
SELECT
  dynpoi_class.source AS source,
  dynpoi_class.item AS item,
  dynpoi_item.menu_en AS menu_en,
  dynpoi_class.title_en AS title_en,
  %s AS count,
  dynpoi_source.comment AS source_comment
FROM dynpoi_class
  LEFT JOIN dynpoi_item
    ON dynpoi_class.item = dynpoi_item.item
  LEFT JOIN dynpoi_source
    ON dynpoi_class.source = dynpoi_source.source
  %s
WHERE 1=1
  %s
GROUP BY
  dynpoi_class.source,
  dynpoi_class.item,
  dynpoi_item.menu_en,
  dynpoi_class.title_en,
  dynpoi_source.comment
ORDER BY
  dynpoi_class.source,
  dynpoi_class.item;
"""

if show_all:
    opt_left_join = "LEFT"
else:
    opt_left_join = ""

if gen == "info":
    opt_count = "count(dynpoi_marker.source)"
    opt_join = """  %s JOIN dynpoi_marker
    ON dynpoi_class.source = dynpoi_marker.source
    AND dynpoi_class.class = dynpoi_marker.class
""" % opt_left_join
elif gen == "false-positive":
    opt_count = "count(dynpoi_status.source)"
    opt_join = """  %s JOIN dynpoi_status
    ON dynpoi_class.source = dynpoi_status.source
    AND dynpoi_class.class = dynpoi_status.class
""" % opt_left_join

opt_where = ""

if source <> None:
    opt_where += " AND dynpoi_class.source = %d" % source
if item <> None:
    opt_where += " AND dynpoi_class.item = %d" % item
if country <> None:
    opt_where += " AND dynpoi_source.comment LIKE '%%%s'" % ("-" + country)

if source == None and item == None and country == None:
    if show_all:
        opt_count = "-1"
    if gen == "info":
        opt_join = ""

sql = sql % (opt_count, opt_join, opt_where)

###########################################################################

print "<table>"
print "<tr>"
print "  <th colspan=\"2\">source</th>"
print "  <th colspan=\"3\">item</th>"
print "  <th>title_en</th>"
print "  <th>count</th>"
print "</tr>"
PgCursor.execute(sql)
total = 0
odd = True
for res in PgCursor.fetchall():
    odd = not odd
    if odd:
        print "<tr class='odd'>"
    else:
        print "<tr class='even'>"

    print "<td><a href=\"?source=%d\">%d</a></td>" % ((res["source"],) * 2)
    cmt_split = res["source_comment"].split("-")
    analyse = "-".join(cmt_split[0:-1])
    country = cmt_split[-1]
    print "<td>%s-<a href=\"?country=%s\">%s</a></td>" % (analyse, country, country)
    print "<td title=\"%s\"><img src=\"/map/markers/marker-l-%d.png\" alt=\"%s\"></td>" % ((res["item"],) * 3)
    print "<td><a href=\"?item=%d\">%d</a>" % ((res["item"],) * 2)
    print "</td>"
    if res["menu_en"]:
        print "<td>%s</td>" % res["menu_en"]
    else:
        print "<td></td>"
    print "<td>%s</td>" % res["title_en"]
    count = res["count"]
    if count == -1:
        count = "N/A"
        total += 1000
    else:
        total += count
    print "<td><a href=\"?source=%d&amp;item=%d\">%s</a></td>" % (res["source"], res["item"], count)
    print "</tr>"
print "</table>"
###########################################################################

if total < 1000:
    sql = """
SELECT
  dynpoi_class.source AS source,
  dynpoi_class.item AS item,
  dynpoi_item.menu_en AS menu_en,
  dynpoi_class.title_en AS title_en,
  dynpoi_source.comment AS source_comment,
  elems AS elems,
  %s AS date,
  subtitle_en AS subtitle_en
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
        opt_date = "-1"
        opt_order = "subtitle_en,"
    elif gen == "false-positive":
        opt_date = "date"
        opt_order = "dynpoi_status.date DESC,"

    sql = sql % (opt_date, opt_join, opt_where, opt_order)

    print "<br>"

    print "<table>"
    print "<tr>"
    print "  <th colspan=\"1\">source</th>"
    print "  <th colspan=\"3\">item</th>"
    print "  <th>elems</th>"
    print "  <th>subtitle</th>"
    if opt_date != "-1":
        print "  <th>date</th>"
    print "</tr>"
    PgCursor.execute(sql)
    odd = True
    for res in PgCursor.fetchall():
        odd = not odd
        if odd:
            print "<tr class='odd'>"
        else:
            print "<tr class='even'>"
        print "<td title=\"%(cmt)s\"><a href=\"?source=%(src)d\">%(src)d</a> </td>" % {"cmt": res["source_comment"], "src": res["source"]}
        print "<td title=\"%(item)d\"><img src=\"/map/markers/marker-l-%(item)d.png\" alt=\"%(item)d\"></td>" % {"item": res["item"]}
        print "<td><a href=\"?item=%d\">%d</a> </td>"%(res["item"],res["item"])
        if res[3]:
            print "<td title=\"%s\">%s</td>" % (res["title_en"], res["menu_en"])
        else:
            print "<td></td>"

        print "<td>"
        if res["elems"]:
            elems = res["elems"].split("_")
            for e in elems:
                m = re.match(r"([a-z]+)([0-9]+)", e)
                if m:
                    print "<b><a target=\"_blank\" href=\"http://www.openstreetmap.org/browse/%s/%s\">%s %s</a></b>"%(m.group(1), m.group(2), m.group(1), m.group(2))

        print "</td>"
        if res["subtitle_en"]:
            print "<td>%s</td>" % res["subtitle_en"]
        else:
            print "<td></td>"
        if opt_date != "-1":
            date = str(res["date"])
            print "<td>%s</td>" % date[:10]
        print "</tr>"
    print "</table>"

###########################################################################
utils.print_tail()
