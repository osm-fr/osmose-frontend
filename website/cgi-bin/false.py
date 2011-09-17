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

###########################################################################
## page headers

print "Content-Type: text/html; charset=utf-8"
print

print "<html>"
print "<head>"
print "  <style type=\"text/css\">"
print "  table"
print "  {"
print "    border-width: 1px 1px 1px 1px;"
print "    border-style: solid;"
print "    border-collapse: collapse;"
print "  }"
print "  td"
print "  {"
print "    border-width: 1px 1px 1px 1px;"
print "    border-style: solid;"
print "    margin: 0px;"
print "    padding: 5px;"
#print "    font-size: -1;"
print "  }"
print "  a:link {"
print "    color: black;"
print "  }"
print "    a:visited {"
print "    color: black;"
print "  }"
print "    a:hover {"
print "    color: black;"
print "  }"
print "  </style>"
print "</head>"
print "<body bgcolor=\"#FFFFFF\">"
print """
<a href="false.py">false.py</a>
<br>
"""
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

#print sql
    
###########################################################################

print "<table>"
print "<tr bgcolor=\"#999999\"><td colspan=\"2\" align=\"center\"><b>source</b></td><td align=\"center\"><b>class</b></td><td colspan=\"3\" align=\"center\"><b>item</b></td><td align=\"center\"><b>title_en</b></td><td align=\"center\"><b>count</b></td></tr>"
PgCursor.execute(sql)
num = 0
odd = True
for res in PgCursor.fetchall():
    num += 1
    odd = not odd
    if odd:
        print "<tr bgcolor=\"#BBBBBB\">"
    else:
        print "<tr bgcolor=\"#EEEEEE\">"        
    print "<td width=\"60\"><a href=\"false.py?source=%d\">%d</a> <a href=\"/map/cgi-bin/index.py?source=%d\">map</a></td>"%(res[0],res[0],res[0])
    print "<td width=\"300\">%s</td>"%res[6]
    print "<td width=\"100\">%d <a href=\"/map/cgi-bin/index.py?source=%d-%d\">map</a> <a href=\"/cgi-bin/graph.py?source=%d&class=%d\">graph</a></td>"%(res[1], res[0], res[1], res[0], res[1])
    if res[3] or not res[2]:
        print "<td width=\"20\"><img src=\"/map/markers/marker-l-%d.png\"></td>"%res[2]
    else:
        print "<td width=\"20\"></td>"
    print "<td width=\"70\"><a href=\"false.py?item=%d\">%d</a> <a href=\"/map/cgi-bin/index.py?item=%d\">map</a></td>"%(res[2],res[2],res[2])
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
  dynpoi_class.source,
  dynpoi_class.class,
  dynpoi_class.item,
  dynpoi_item.menu_en,
  dynpoi_class.title_en,
  dynpoi_source.comment,
  dynpoi_status.elems AS elems,
  dynpoi_status.date,
  dynpoi_status.subtitle_en
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

    print "<table>"
    print "<tr bgcolor=\"#999999\"><td colspan=\"1\" align=\"center\"><b>source</b></td><td align=\"center\"><b>class</b></td><td colspan=\"3\" align=\"center\"><b>item</b></td><td align=\"center\"><b>elems</b></td><td align=\"center\"><b>subtitle</b><td align=\"center\"><b>date</b></td></tr>"
    PgCursor.execute(sql)
    odd = True
    for res in PgCursor.fetchall():
        num += 1
        odd = not odd
        if odd:
            print "<tr bgcolor=\"#BBBBBB\">"
        else:
            print "<tr bgcolor=\"#EEEEEE\">"        
        print "<td title=\"%s\"><a href=\"false.py?source=%d\">%d</a> </td>"%(res[5],res[0],res[0])
        print "<td>%d </td>"%(res[1])
        if res[3] or not res[2]:
            print "<td><img src=\"/map/markers/marker-l-%d.png\"></td>"%res[2]
        else:
            print "<td></td>"
        print "<td><a href=\"false.py?item=%d\">%d</a> </td>"%(res[2],res[2])
        if res[3]:
            print "<td>%s</td>"%res[3]
        else:
            print "<td></td>"

        print "<td>"
        elems = res["elems"].split("_")
        for e in elems:
            m = re.match(r"([a-z]+)([0-9]+)", e)
            if m:
                print "<b><a target=\"_blank\" href=\"http://www.openstreetmap.org/browse/%s/%s\">%s %s</a></b>"%(m.group(1), m.group(2), m.group(1), m.group(2))

        print "</td>"
        print "<td>%s</td>"%res[8]
        print "<td>%s</td>"%res[7]
        print "</tr>"
    print "</table>"


###########################################################################
print "</body>"
