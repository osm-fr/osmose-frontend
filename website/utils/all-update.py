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

import sys, os, time, cgi
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

PgConn   = utils.get_dbconn()
PgCursor = PgConn.cursor()

form   = cgi.FieldStorage()
source = int(form.getvalue("source", "0"))

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

###########################################################################
## get timestamps
lasts = {}
if source:
    sql = "SELECT source,timestamp,remote_url,remote_ip FROM dynpoi_update WHERE source=%d ORDER BY timestamp DESC;"%source
else:
    sql = "SELECT source,timestamp,remote_url,remote_ip FROM dynpoi_update ORDER BY timestamp DESC;"
PgCursor.execute(sql)

#name = lasts[int(source_id)]["remote_url"].split("/")[-1].split(".")[0].lower()
#age  = lasts[int(source_id)]["age"] # now - time.mktime(time.strptime(str(lasts[int(source_id)]["timestamp"]),"%Y-%m-%dT%H:%M:%SZ"))
#txt  = "il y a %dj, %dh, %02dm"%(int(age/86400), int(age/3600)%24, int(age/60)%60)

print "<table>"
print "<tr bgcolor=\"#999999\"><td><b>source</b></td><td><b>remote url</b></td><td><b>timestamp</b></td></tr>"
odd = True
for res in PgCursor.fetchall():
    odd = not odd
    if odd:
        print "<tr bgcolor=\"#BBBBBB\">"
    else:
        print "<tr bgcolor=\"#EEEEEE\">"        
    print "<td width=\"50\"><a href=\"info.py?source=%s\">%s</a></td>"%(res[0],res[0])
    url = res[2]
    url = url.replace("http://cedric.dumez-viou.fr", "http://cdv")
    url = url.replace("http://osm1.crans.org", "http://osm1")
    url = url.replace("http://osm2.crans.org", "http://osm2")
    url = url.replace("http://osm3.crans.org", "http://osm3")
    url = url.replace("http://osm4.crans.org", "http://osm4")
    url = url.replace("http://osm5.univ-nantes.fr", "http://osm5")
    url = url.replace("http://osm6.univ-nantes.fr", "http://osm6")
    url = url.replace("http://osm7.pole-aquinetic.fr", "http://osm7")
    url = url.replace("http://osm8.pole-aquinetic.fr", "http://osm8")
    print "<td width=\"800\">%s</td>"%url
    print "<td width=\"200\">%s</td>"%res[1]
    print "</tr>"
print "</table>"

###########################################################################
print "</body>"
