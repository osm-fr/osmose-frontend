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

form   = cgi.FieldStorage()
source = form.getvalue("source", "")
item   = form.getvalue("item", "")

if source:
    source = int(source)
    item   = None
elif item:
    source = None
    item   = int(item)
else:
    source = None
    item   = None

if "false-positive" in os.environ["SCRIPT_NAME"]:
    gen = "false-positive"
elif "info" in os.environ["SCRIPT_NAME"]:
    gen = "info"


###########################################################################
## page headers

utils.print_header()

print "<a href=\"false-positive.py\">Accueil des faux positifs</a><br>"
print "<a href=\"\">Faux positifs</a> <a href=\"info.py?%s\">Informations</a>" % os.environ["QUERY_STRING"]
print "<br><br>"

###########################################################################

sql = """
select
  dynpoi_class.source,
  dynpoi_class.class,
  dynpoi_class.item,
  dynpoi_item.menu_en,
  dynpoi_class.title_en,
  count(dynpoi_status.source),
  dynpoi_source.comment
from dynpoi_class
  left join dynpoi_item
    on dynpoi_class.item = dynpoi_item.item
  join dynpoi_status
    on dynpoi_class.source = dynpoi_status.source
    and dynpoi_class.class = dynpoi_status.class
    and dynpoi_status.status = 'false'
  left join dynpoi_source
    on dynpoi_class.source = dynpoi_source.source
%s
group by
  dynpoi_class.source,
  dynpoi_class.class,
  dynpoi_class.item,
  dynpoi_item.menu_en,
  dynpoi_class.title_en,
  dynpoi_source.comment
order by
  dynpoi_class.item,
  dynpoi_class.source,
  dynpoi_class.class
"""

if source <> None:
    sql = sql%"WHERE dynpoi_class.source = %d"%source
elif item <> None:
    sql = sql%"WHERE dynpoi_class.item = %d"%item
else:
    sql = sql%""

###########################################################################

print "<table>"
print "<tr>"
print "  <th colspan=\"2\">source</th>"
print "  <th>class</th>"
print "  <th colspan=\"3\">item</th>"
print "  <th>title_en</th>"
print "  <th>count</th>"
print "</tr>"
PgCursor.execute(sql)
num = 0
odd = True
for res in PgCursor.fetchall():
    num += 1
    odd = not odd
    if odd:
        print "<tr class='odd'>"
    else:
        print "<tr class='even'>"

    print "<td width=\"60\"><a href=\"?source=%d\">%d</a> <a href=\"/map/?source=%d\">map</a></td>"%(res[0],res[0],res[0])
    print "<td width=\"300\">%s</td>"%res[6]
    print "<td width=\"100\">%d <a href=\"/map/?source=%d-%d\">map</a> <a href=\"graph.py?source=%d&amp;class=%d\">graph</a></td>"%(res[1], res[0], res[1], res[0], res[1])
    print "<td title=\"%s\"><img src=\"/map/markers/marker-l-%d.png\" alt=\"%s\"></td>" % (res[2], res[2], res[2])
    print "<td width=\"70\"><a href=\"?item=%d\">%d</a> <a href=\"/map/?item=%d\">map</a></td>"%(res[2],res[2],res[2])
    if res[3]:
        print "<td width=\"150\">%s</td>"%res[3]
    else:
        print "<td width=\"150\"></td>"
    print "<td width=\"300\">%s</td>"%res[4]
    print "<td width=\"50\">%d</td>"%res[5]
    print "</tr>"
print "</table>"


if num < 50:
    sql = """
select
  dynpoi_class.source AS source,
  dynpoi_class.class AS class,
  dynpoi_class.item AS item,
  dynpoi_item.menu_en AS menu_en,
  dynpoi_class.title_en AS title_en,
  dynpoi_source.comment AS source_comment,
  dynpoi_status.elems AS elems,
  dynpoi_status.date AS date,
  dynpoi_status.subtitle_en AS subtitle_en
from dynpoi_class
  left join dynpoi_item
    on dynpoi_class.item = dynpoi_item.item
  join dynpoi_status
    on dynpoi_class.source = dynpoi_status.source
    and dynpoi_class.class = dynpoi_status.class
    and dynpoi_status.status = 'false'
  left join dynpoi_source
    on dynpoi_class.source = dynpoi_source.source
%s
order by
  dynpoi_status.date DESC,
  dynpoi_class.item,
  dynpoi_class.source,
  dynpoi_class.class
"""

    if source <> None:
        sql = sql%"WHERE dynpoi_class.source = %d"%source
    elif item <> None:
        sql = sql%"WHERE dynpoi_class.item = %d"%item
    else:
        sql = sql%""

    print "<br>"

    print "<table>"
    print "<tr>"
    print "  <th colspan=\"1\">source</th>"
    print "  <th>class</th>"
    print "  <th colspan=\"3\">item</th>"
    print "  <th>elems</th>"
    print "  <th>subtitle</th>"
    print "  <th>date</th>"
    print "</tr>"
    PgCursor.execute(sql)
    odd = True
    for res in PgCursor.fetchall():
        num += 1
        odd = not odd
        if odd:
            print "<tr class='odd'>"
        else:
            print "<tr class='even'>"
        print "<td title=\"%(cmt)s\"><a href=\"?source=%(src)d\">%(src)d</a> </td>" % {"cmt": res["source_comment"], "src": res["source"]}
        print "<td>%d</td>"%(res["class"])
        print "<td title=\"%(item)d\"><img src=\"/map/markers/marker-l-%(item)d.png\" alt=\"%(item)d\"></td>" % {"item": res["item"]}
        print "<td><a href=\"?item=%d\">%d</a> </td>"%(res["item"],res["item"])
        if res[3]:
            print "<td title=\"%s\">%s</td>" % (res["title_en"], res["menu_en"])
        else:
            print "<td></td>"

        print "<td>"
        elems = res["elems"].split("_")
        for e in elems:
            m = re.match(r"([a-z]+)([0-9]+)", e)
            if m:
                print "<b><a target=\"_blank\" href=\"http://www.openstreetmap.org/browse/%s/%s\">%s %s</a></b>"%(m.group(1), m.group(2), m.group(1), m.group(2))

        print "</td>"
        print "<td>%s</td>"%res["subtitle_en"]
        date = str(res["date"])
        print "<td>%s</td>" % date[:10]
        print "</tr>"
    print "</table>"


###########################################################################
utils.print_tail()
