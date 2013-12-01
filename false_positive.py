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

from bottle import route, request, template, response, abort, delete
import StringIO, os, tempfile, urllib2

from tools import osmose_common
from tools import utils
from tools import tag2link

t2l = tag2link.tag2link("tools/tag2link_sources.xml")


def _get(db, err_id, status):
    columns = ["item", "source", "class", "elems", "subclass",
        "lat", "lon",
        "title", "subtitle",
        "dynpoi_status.date", "dynpoi_class.timestamp"]
    sql = "SELECT " + ",".join(columns) + """
    FROM
        dynpoi_status
        JOIN dynpoi_class USING (source,class)
    WHERE
        dynpoi_status.status = %s AND
        dynpoi_status.id = %s
    """
    db.execute(sql, (status, err_id, ))
    marker = db.fetchone()

    if not marker:
        abort(410, "Id is not present in database.")

    return (marker, columns)


@route('/false-positive/<err_id:int>')
def fp_(db, lang, err_id):
    (marker, columns) = _get(db, err_id, 'false')

    return template('false-positive/index', err_id=err_id, marker=marker, columns_marker=columns)


@route('/api/0.2/false-positive/<err_id:int>')
def fp(db, lang, err_id):
    data_type = { "N": "node", "W": "way", "R": "relation", "I": "infos"}

    # TRANSLATORS: link to tooltip help
    url_help = _("http://wiki.openstreetmap.org/wiki/Osmose/errors")

    translate = utils.translator(lang)

    (marker, columns) = _get(db, err_id, 'false')

    lat       = str(marker["lat"])
    lon       = str(marker["lon"])
    title     = translate.select(marker["title"])
    subtitle  = translate.select(marker["subtitle"])
    b_date    = marker["timestamp"] or ""
    item      = marker["item"] or 0
    date      = marker["date"].isoformat() or 0

    return {
        "lat":lat, "lon":lon,
        "minlat": float(lat) - 0.002, "maxlat": float(lat) + 0.002,
        "minlon": float(lon) - 0.002, "maxlon": float(lon) + 0.002,
        "error_id":err_id,
        "title":title, "subtitle":subtitle,
        "b_date":b_date.strftime("%Y-%m-%d"),
        "item":item,
        "date":date,
        "url_help":url_help
    }


@delete('/api/0.2/false-positive/<err_id:int>')
def fp_delete(db, err_id):

    sql = """SELECT id FROM dynpoi_status
    WHERE
        status = %s AND
        id = %s
    """
    db.execute(sql, ('false', err_id, ))
    m = db.fetchone()
    if not m:
        abort(410, "FAIL")

    sql = """DELETE FROM dynpoi_status
    WHERE
        status = %s AND
        id = %s
    """
    db.execute(sql, ('false', err_id, ))
    db.connection.commit()

    return
