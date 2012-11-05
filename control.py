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

from bottle import route, request, response, template, post
from tools import utils
import tools.update
import os
import sys

@route('/control/update')
def updates(db):
    db.execute("""
SELECT DISTINCT ON (source)
    source,
    EXTRACT(EPOCH FROM ((now())-timestamp)) AS age,
    remote_url,
    remote_ip
FROM
    dynpoi_update
ORDER BY
    source ASC,
    timestamp DESC
""")
    lasts = {}
    for res in db.fetchall():
        lasts[int(res["source"])] = res

    sources = utils.get_sources()

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

    return template('control/updates', liste=liste)


@route('/control/update/<source:int>')
def update(db, source=None):
    sql = "SELECT source,timestamp,remote_url,remote_ip FROM dynpoi_update WHERE source=%d ORDER BY timestamp DESC;" % source
    db.execute(sql)
    return template('control/update', liste=db.fetchall())


@route('/control/i18n')
def update():
    return os.popen("cd po && make statistics | sed -n '1h;2,$H;${g;s/\\n/<br>/g;p}'").read()


@route('/control/lang')
def update(lang):
    out = request.headers['Accept-Language'] + "\n"
    out += "\n".join(lang)
    response.content_type = "text/plain; charset=utf-8"
    return out


@post('/control/send-update')
@post('/cgi-bin/update.py') # Backward compatibility
def send_update():
    code = request.params.get('code')
    url = request.params.get('url')

    response.content_type = "text/plain; charset=utf-8"

    if not code or not url:
        return "FAIL"

    sources = utils.get_sources()
    for s in sources:
        if sources[s].get("updatecode", 0) <> code:
            continue
        try:
            tools.update.update(sources[s], url)
        except:
            import traceback
            from cStringIO import StringIO
            import smtplib
            s = StringIO()
            sys.stderr = s
            traceback.print_exc()
            sys.stderr = sys.__stderr__
            traceback = s.getvalue()
            return traceback.rstrip()

        return "OK"

    return "AUTH FAIL"
