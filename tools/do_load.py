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

import sys, os, cgi, Cookie, datetime, utils, time

PgConn   = utils.get_dbconn()
PgCursor = PgConn.cursor()

all = set()
sql = "SELECT dynpoi_marker.source, dynpoi_marker.class, dynpoi_marker.elems, dynpoi_marker.subclass, marker_id FROM dynpoi_marker WHERE source=3;"
PgCursor.execute(sql)

while True:
    data = PgCursor.fetchmany(1000)
    if not data:
        break
    for res in data:
        error_id = "%d-%d-%d-%s-%d" % (res["source"], res["class"], res["subclass"], res["elems"], res["marker_id"])
        all.add(error_id)
