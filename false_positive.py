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


def _get(db, status, err_id=None, uuid=None):
    columns = ["item", "source", "class", "subclass",
        "lat", "lon",
        "title", "subtitle",
        "dynpoi_status.date", "dynpoi_class.timestamp"]

    if err_id:
        sql = "SELECT " + ",".join(columns) + """
        FROM
            dynpoi_status
            JOIN dynpoi_class USING (source,class)
        WHERE
            dynpoi_status.status = %s AND
            dynpoi_status.id = %s
        """
        db.execute(sql, (status, err_id))
    else:
        sql = "SELECT " + ",".join(columns) + """
        FROM
            dynpoi_status
            JOIN dynpoi_class USING (source,class)
        WHERE
            dynpoi_status.status = %s AND
            dynpoi_status.uuid = %s
        """
        db.execute(sql, (status, uuid))

    marker = db.fetchone()

    if not marker:
        abort(410, "Id is not present in database.")

    return (marker, columns)


@route('/false-positive/<uuid:uuid>')
def fp_(db, lang, uuid):
    (marker, columns) = _get(db, 'false', uuid=uuid)

    return template('false-positive/index', translate=utils.translator(lang), uuid=uuid, marker=marker, columns_marker=columns)


@route('/api/0.2/false-positive/<err_id:int>')
def fp_err_id(db, lang, err_id):
    return _fp(2, db, lang, None, *_get(db, 'false', err_id=err_id))

@route('/api/0.3beta/false-positive/<uuid:uuid>')
def fp_uuid(db, lang, uuid):
    return _fp(3, db, lang, uuid, *_get(db, 'false', uuid=uuid))

def _fp(version, db, lang, uuid, marker, columns):
    data_type = { "N": "node", "W": "way", "R": "relation", "I": "infos"}

    # TRANSLATORS: link to tooltip help
    url_help = _("http://wiki.openstreetmap.org/wiki/Osmose/errors")

    translate = utils.translator(lang)

    lat       = str(marker["lat"])
    lon       = str(marker["lon"])
    title     = translate.select(marker["title"])
    subtitle  = translate.select(marker["subtitle"])
    b_date    = marker["timestamp"] or ""
    item      = marker["item"] or 0
    date      = marker["date"].isoformat() or 0

    if version == 2:
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
    else:
        return {
            "lat":lat, "lon":lon,
            "minlat": float(lat) - 0.002, "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002, "maxlon": float(lon) + 0.002,
            "id":uuid,
            "title":title, "subtitle":subtitle,
            "b_date":b_date.strftime("%Y-%m-%d"),
            "item":item,
            "date":date,
            "url_help":url_help
        }


@delete('/api/0.2/false-positive/<err_id:int>')
def fp_delete_err_id(db, err_id):
    db.execute("SELECT id FROM dynpoi_status WHERE status = %s AND id = %s", ('false', err_id))
    m = db.fetchone()
    if not m:
        abort(410, "FAIL")

    db.execute("DELETE FROM dynpoi_status WHERE status = %s AND id = %s", ('false', err_id))
    db.connection.commit()

    return

@delete('/api/0.3beta/false-positive/<uuid:uuid>')
def fp_delete_uuid(db, uuid):
    db.execute("SELECT id FROM dynpoi_status WHERE status = %s AND uuid = %s", ('false', uuid))
    m = db.fetchone()
    if not m:
        abort(410, "FAIL")

    db.execute("DELETE FROM dynpoi_status WHERE status = %s AND uuid = %s", ('false', uuid))
    db.connection.commit()

    return
