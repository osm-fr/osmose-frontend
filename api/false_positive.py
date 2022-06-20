#! /usr/bin/env python
# -*- coding: utf-8 -*-
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

from bottle import abort, default_app, delete, route

from modules import utils

from .false_positive_utils import _get

app_0_2 = default_app.pop()


@app_0_2.route("/false-positive/<err_id:int>")
def fp_err_id(db, lang, err_id):
    marker, columns = _get(db, "false", err_id=err_id)
    if not marker:
        abort(410, "Id is not present in database.")

    return _fp(2, db, lang, None, marker, columns)


@route("/false-positive/<uuid:uuid>")
def fp_uuid(db, langs, uuid):
    marker, columns = _get(db, "false", uuid=uuid)
    if not marker:
        abort(410, "Id is not present in database.")

    return _fp(3, db, langs, uuid, marker, columns)


def _fp(version, db, langs, uuid, marker, columns):
    lat = str(marker["lat"])
    lon = str(marker["lon"])
    title = utils.i10n_select(marker["title"], langs)
    subtitle = utils.i10n_select(marker["subtitle"], langs)
    item = marker["item"] or 0
    date = marker["date"].isoformat() or 0

    if version == 2:
        return {
            "lat": lat,
            "lon": lon,
            "minlat": float(lat) - 0.002,
            "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002,
            "maxlon": float(lon) + 0.002,
            "error_id": err_id,
            "title": title["auto"],
            "subtitle": subtitle["auto"],
            "b_date": None,  # Keep for retro compatibility
            "item": item,
            "date": date,
            "url_help": "",  # Keep for retro compatibility
        }
    else:
        return {
            "lat": lat,
            "lon": lon,
            "minlat": float(lat) - 0.002,
            "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002,
            "maxlon": float(lon) + 0.002,
            "id": uuid,
            "title": title,
            "subtitle": subtitle,
            "b_date": None,  # Keep for retro compatibility
            "item": item,
            "date": date,
        }


@app_0_2.delete("/false-positive/<err_id:int>")
def fp_delete_err_id(db, err_id):
    db.execute(
        "SELECT uuid FROM markers_status WHERE status = %s AND uuid_to_bigint(markers_status.uuid) = %s",
        ("false", err_id),
    )
    m = db.fetchone()
    if not m:
        abort(410, "FAIL")

    db.execute(
        "DELETE FROM markers_status WHERE status = %s AND uuid_to_bigint(markers_status.uuid) = %s",
        ("false", err_id),
    )
    db.connection.commit()

    return


@delete("/false-positive/<uuid:uuid>")
def fp_delete_uuid(db, uuid):
    db.execute(
        "SELECT uuid FROM markers_status WHERE status = %s AND uuid = %s",
        ("false", uuid),
    )
    m = db.fetchone()
    if not m:
        abort(410, "FAIL")

    db.execute(
        "DELETE FROM markers_status WHERE status = %s AND uuid = %s", ("false", uuid)
    )
    db.connection.commit()

    return


default_app.push(app_0_2)
