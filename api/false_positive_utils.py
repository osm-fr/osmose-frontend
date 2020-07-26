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
    columns = ["item", "markers_status.source_id", "class",
        "lat", "lon",
        "title", "subtitle",
        "markers_status.date", "markers_counts.timestamp"]

    if err_id:
        sql = "SELECT " + ",".join(columns) + """
        FROM
            markers_status
            JOIN markers_counts ON
                markers_counts.source_id = markers_status.source_id AND
                markers_counts.class = markers_status.class
            JOIN class USING (item, class)
        WHERE
            markers_status.status = %s AND
            uuid_to_bigint(markers_status.uuid) = %s
        """
        db.execute(sql, (status, err_id))
    else:
        sql = "SELECT " + ",".join(columns) + """
        FROM
            markers_status
            JOIN markers_counts ON
                markers_counts.source_id = markers_status.source_id AND
                markers_counts.class = markers_status.class
            JOIN class USING (item, class)
        WHERE
            markers_status.status = %s AND
            markers_status.uuid = %s
        """
        db.execute(sql, (status, uuid))

    marker = db.fetchone()

    if not marker:
        abort(410, "Id is not present in database.")

    return (marker, columns)
