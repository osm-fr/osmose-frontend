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

###########################################################################
## page headers

translate = utils.translator()
show = utils.show
utils.print_header(_("OsmOse - Users statistics"))

###########################################################################

sql = """--
SELECT count(*) AS cpt,
       username
FROM marker_elem
GROUP BY username
ORDER BY cpt DESC
LIMIT 500;"""

show(u"<table class='byuser'>\n")
show(u"  <tr>\n")
show(u"    <th>%s</th>\n" % _("Number"))
show(u"    <th>%s</th>\n" % _("Username"))
show(u"  </tr>\n")

PgCursor.execute(sql)

for res in PgCursor.fetchall():
    show(u"  <tr>\n")
    show(u"    <td>" + unicode(res["cpt"]) + u"</td>\n")
    show(u"    <td>" + unicode(res["username"]) + u"</td>\n")
    show(u"  </tr>\n")

show(u"</table>\n")

###########################################################################
utils.print_tail()
