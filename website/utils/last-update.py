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

translate = utils.translator()
show = utils.show

###########################################################################
## page headers


utils.print_header(_("OsmOse - last updates"))

###########################################################################
## get timestamps
lasts = {}
sql = """SELECT DISTINCT ON (source)
                source,
                EXTRACT(EPOCH FROM ((now())-timestamp)) AS age,
                remote_url,remote_ip
         FROM dynpoi_update
         ORDER BY source ASC, timestamp DESC;"""
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
        age  = lasts[int(source_id)]["age"]
        if age >= 0:
            # TRANSLATORS: days / hours / minutes since last source update, abbreviated to d / h / m
            txt = _("{day}d, {hour}h, {minute}m ago").format(day=int(age/86400), hour=int(age/3600)%24, minute=int(age/60)%60)
        else:
            txt = _("in {day}d, {hour}h, {minute}m").format(day=int(-age/86400), hour=int(-age/3600)%24, minute=int(-age/60)%60)
        
        liste.append((sources[source_id]["comment"], age, txt, source_id))
    else:
        liste.append((sources[source_id]["comment"], 1e10, _("never generated"), source_id))
liste.sort(lambda x, y: -cmp(x[1], y[1]))

#f = open("/tmp/update.sql", "w")
#for x in liste:
#    f.write("UPDATE dynpoi_source SET comment='%s' WHERE source = %d;\n"%(utils.pg_escape(x[0][9:]), int(x[3])))
#f.close()

show(u"<table>")
show(u"<tr bgcolor=\"#999999\">")
show(u"<td>%s</td>" % _("source"))
show(u"<td>%s</td>" % _("description"))
show(u"<td>%s</td>" % _("last generation"))
show(u"</td><td>%s</td>" % _("history"))
show(u"</tr>")
odd = True
for source in liste:
    odd = not odd
    if odd:
        show(u"<tr bgcolor=\"#BBBBBB\">")
    else:
        show(u"<tr bgcolor=\"#EEEEEE\">"        )
    show(u"<td width=\"50\"><a href=\"info.py?source=%s\">%s</a></td>"%(source[3],source[3]))
    show(u"<td width=\"600\">%s</td>" % source[0])
    show(u"<td width=\"200\">%s</td>" % source[2])
    show(u"<td width=\"30\"><a href=\"all-update.py?source=%s\">%s</a></td>" % (source[3], _("history")))
    show(u"</tr>")
show(u"</table>")

###########################################################################
utils.print_tail()
