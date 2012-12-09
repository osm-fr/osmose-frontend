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
SELECT DISTINCT ON (dynpoi_source.source)
    dynpoi_source.source,
    EXTRACT(EPOCH FROM ((now())-dynpoi_update.timestamp)) AS age,
    dynpoi_source.comment
FROM
    dynpoi_source
    LEFT JOIN dynpoi_update ON
        dynpoi_source.source = dynpoi_update.source
ORDER BY
    dynpoi_source.source ASC,
    dynpoi_update.timestamp DESC
""")
    liste = []
    for res in db.fetchall():
        source, age, comment = res
        if age:
            if age >= 0:
                # TRANSLATORS: days / hours / minutes since last source update, abbreviated to d / h / m
                txt = _("{day}d, {hour}h, {minute}m ago").format(day=int(age/86400), hour=int(age/3600)%24, minute=int(age/60)%60)
            else:
                txt = _("in {day}d, {hour}h, {minute}m").format(day=int(-age/86400), hour=int(-age/3600)%24, minute=int(-age/60)%60)
            liste.append((comment, age, txt, source))
        else:
            liste.append((comment, 1e10, _("never generated"), source))
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
    src = request.params.get('src', default=None)
    code = request.params.get('code')
    url = request.params.get('url')

    response.content_type = "text/plain; charset=utf-8"

    if not code or not url:
        return "FAIL"

    sources = utils.get_sources()
    for s in sources:
        if src and sources[s]["comment"] != src:
            continue
        if sources[s]["updatecode"] != code:
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
