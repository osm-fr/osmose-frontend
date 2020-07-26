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

from modules import utils

if __name__ == "__main__":

    sources = [int(x) for x in utils.get_sources().keys()]
    dbconn  = utils.get_dbconn()
    dbcurs  = dbconn.cursor()

    tables  = ["markers_counts", "markers", "markers_status", "updates"]
    for t in tables:
        dbcurs.execute("SELECT source_id FROM %s GROUP BY source_id;"%t)
        for res in dbcurs.fetchall():
            if res[0] not in sources:
                print("DELETE FROM %s WHERE source_id = %d;"%(t, res[0]))
