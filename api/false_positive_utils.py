#! /usr/bin/env python
#-*- coding: utf-8 -*-
###########################################################################
##                                                                       ##
## Copyrights Jocelyn Jaubert 2013                                       ##
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

def _get(db, status, err_id=None, uuid=None):
    columns = [
        "markers_status.item", "source_id", "markers_status.class",
        "lat::float", "lon::float",
        "title", "subtitle",
        "date",
    ]

    if err_id:
        sql = "SELECT " + ",".join(columns) + """
        FROM
            markers_status
            JOIN class ON
                class.item = markers_status.item AND
                class.class = markers_status.class
        WHERE
            status = %s AND
            uuid_to_bigint(uuid) = %s
        """
        db.execute(sql, (status, err_id))
    else:
        sql = "SELECT " + ",".join(columns) + """
        FROM
            markers_status
        JOIN class ON
            class.item = markers_status.item AND
            class.class = markers_status.class
        WHERE
            status = %s AND
            uuid = %s
        """
        db.execute(sql, (status, uuid))

    marker = db.fetchone()

    return (marker, columns)
