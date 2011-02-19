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

import sys, os, time
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

PgConn   = utils.get_dbconn()
PgCursor = PgConn.cursor()

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
sql = "SELECT DISTINCT ON (source) source,EXTRACT(EPOCH FROM now()-timestamp) AS age,remote_url,remote_ip FROM dynpoi_update ORDER BY source ASC, timestamp DESC;"
PgCursor.execute(sql)
for res in PgCursor.fetchall():
    lasts[int(res["source"])] = res

###########################################################################
## get sources
sources = utils.get_sources()
categs  = utils.get_categories()
dbconn  = utils.get_dbconn()
dbcurs  = dbconn.cursor()

###########################################################################


liste = []
for source_id in [str(y) for y in sorted([int(x) for x in sources])]:
    like = sources[source_id].get("like", source_id)
    if int(source_id) in lasts:
        #name = lasts[int(source_id)]["remote_url"].split("/")[-1].split(".")[0].lower()
        age  = lasts[int(source_id)]["age"] - 7200# now - time.mktime(time.strptime(str(lasts[int(source_id)]["timestamp"]),"%Y-%m-%dT%H:%M:%SZ"))
        #txt  = "il y a %dh%02d"%(int(age/3600), int((age%3600)/60))
        txt  = "il y a %dj, %dh, %02dm"%(int(age/86400), int(age/3600)%24, int(age/60)%60)
        
        liste.append((sources[source_id]["comment"], age, txt, source_id))
    else:
        liste.append((sources[source_id]["comment"], 0, "jamais généré", source_id))
liste.sort(lambda x, y: -cmp(x[1], y[1]))

#f = open("/tmp/update.sql", "w")
#for x in liste:
#    f.write("UPDATE dynpoi_source SET comment='%s' WHERE source = %d;\n"%(utils.pg_escape(x[0][9:]), int(x[3])))
#f.close()

print "<table>"
print "<tr bgcolor=\"#999999\"><td><b>source</b></td><td><b>description</b></td><td><b>Dernière génération</b></td><td><b>all</b></td></tr>"
odd = True
for source in liste:
    odd = not odd
    if odd:
        print "<tr bgcolor=\"#BBBBBB\">"
    else:
        print "<tr bgcolor=\"#EEEEEE\">"        
    print "<td width=\"50\"><a href=\"info.py?source=%s\">%s</a></td>"%(source[3],source[3])
    print "<td width=\"600\">%s</td>"%source[0]
    print "<td width=\"200\">%s</td>"%(source[2])
    print "<td width=\"30\"><a href=\"all-update.py?source=%s\">all</a></td>"%(source[3])
    print "</tr>"
print "</table>"

###########################################################################
print "</body>"
