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

from bottle import route, request, response, post, HTTPError, abort
from modules import utils
from . import update
import os
import sys


@post('/send-update')
def send_update(db):
    src = request.params.get('source', default=None) # Deprecated, replaced by analyser & country
    analyser = request.params.get('analyser', default=None)
    country = request.params.get('country', default=None)
    code = request.params.get('code')
    upload = request.files.get('content', default=None)

    response.content_type = "text/plain; charset=utf-8"

    if not code or not upload:
        abort(401, 'FAIL')

    if src:
        # Deprecated, replaced by analyser & country
        analyser, country = src.rsplit("-", 1)

    db.execute("""
SELECT
    id
FROM
    source
    JOIN source_password ON
        source.id = source_id
WHERE
    analyser = %(analyser)s AND
    country = %(country)s AND
    password = %(password)s
LIMIT 1
""", {"analyser": analyser, "country": country, "password": code})

    res = db.fetchone()

    if not res and not os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        abort(403, 'AUTH FAIL')
    if not res and os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        r = db.execute("SELECT COALESCE(MAX(id), 0) + 1 AS id FROM source")
        source_id = db.fetchone()["id"]
        db.execute("INSERT INTO source(id, country, analyser) VALUES (%s, %s, %s)", (source_id, country, analyser))
        db.execute("INSERT INTO source_password(source_id, password) VALUES(%s, %s)", (source_id, code))
        db.connection.commit()
    else:
        source_id = res["id"]

    remote_ip = request.remote_addr

    try:
        (name, ext) = os.path.splitext(upload.filename)
        if ext not in ('.bz2','.gz','.xml'):
            abort(406, 'FAIL: File extension not allowed.')

        save_filename = os.path.join(utils.dir_results, upload.filename)
        upload.save(save_filename, overwrite=True)
        update.update(source_id, save_filename, remote_ip=remote_ip)
        os.unlink(save_filename)

    except update.OsmoseUpdateAlreadyDone:
        abort(409, 'FAIL: Already up to date')

    except:
        import traceback
        from io import StringIO
        import smtplib
        s = StringIO()
        sys.stderr = s
        traceback.print_exc()
        sys.stderr = sys.__stderr__
        traceback = s.getvalue()
        return traceback.rstrip()

    return "OK"

def _status_object(db, t, source):
    db.execute('SELECT elem->''id'' FROM (SELECT unnest(elems) AS elem FROM marker WHERE source=1) AS t WHERE elem->''type'' = ''"%s"''::jsonb', (source, t))
    s = db.fetchone()
    if s and s[0]:
        return list(map(int, s[0].split(',')))

@route('/status/<country>/<analyser>')
def status(db, country = None, analyser = None):
    if not country or not analyser:
        return HTTPError(400)

    objects = request.params.get('objects', default=False)

    db.execute('SELECT timestamp, source, analyser_version FROM dynpoi_update_last WHERE source = (SELECT id FROM source WHERE analyser = %s AND country = %s)', (analyser, country))
    r = db.fetchone()
    if r and r['timestamp']:
        return {
           'version': 1,
           'timestamp': str(r['timestamp'].replace(tzinfo=None)),
           'analyser_version': str(r['analyser_version'] or ''),
           'nodes': _status_object(db, 'N', r['source']) if objects != False else None,
           'ways': _status_object(db, 'W', r['source']) if objects != False else None,
           'relations': _status_object(db, 'R', r['source']) if objects != False else None,
        }
    else:
        return HTTPError(404)
