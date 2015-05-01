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
from collections import defaultdict

@route('/control/update')
def updates(db, lang):
    db.execute("""
SELECT
    source.id,
    EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp)) AS age,
    source.country,
    source.analyser
FROM
    source
    LEFT JOIN dynpoi_update_last ON
        source.id = dynpoi_update_last.source
ORDER BY
    dynpoi_update_last.timestamp DESC
""")
    liste = []
    for res in db.fetchall():
        (source, age, country, analyser) = (res[0], res[1], res[2], res[3])
        if age:
            if age >= 0:
                # TRANSLATORS: days / hours / minutes since last source update, abbreviated to d / h / m
                txt = _("{day}d, {hour}h, {minute}m ago").format(day=int(age/86400), hour=int(age/3600)%24, minute=int(age/60)%60)
            else:
                txt = _("in {day}d, {hour}h, {minute}m").format(day=int(-age/86400), hour=int(-age/3600)%24, minute=int(-age/60)%60)
            liste.append((country, analyser, age, txt, source))
        else:
            liste.append((country, analyser, 1e10, _("never generated"), source))
    liste.sort(lambda x, y: -cmp(x[2], y[2]))

    return template('control/updates', liste=liste)


@route('/control/update_matrix')
def updates(db, lang):
    remote = request.params.get('remote')
    country = request.params.get('country')
    db.execute("""
SELECT DISTINCT ON (source.id)
    source.id,
    EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp)) AS age,
    country,
    analyser
FROM
    source
    JOIN dynpoi_update_last ON
        source.id = dynpoi_update_last.source """ + (
"""
    JOIN dynpoi_update ON
        dynpoi_update.source = dynpoi_update_last.source AND
        dynpoi_update.timestamp = dynpoi_update_last.timestamp """ if remote else "") + """
WHERE
""" + ("""
    RIGHT(MD5(remote_ip), 4) = %(remote)s AND """ if remote else "") + ("""
    source.country LIKE %(country)s AND """ if country else "") + """
    true
ORDER BY
    source.id ASC,
    dynpoi_update_last.timestamp DESC
""", {"remote": remote, "country": country and country.replace("*", "%")})

    keys = defaultdict(int)
    matrix = defaultdict(dict)
    stats_analyser = {}
    stats_country = {}
    for res in db.fetchall():
        (source, age, country, analyser) = (res[0], res[1], res[2], res[3])
        keys[country] += 1
        matrix[analyser][country] = (age/60/60/24, source)
    for analyser in matrix:
        min = max = None
        sum = 0
        for country in matrix[analyser]:
            v = matrix[analyser][country][0]
            min = v if not min or v < min else min
            max = v if not max or v > max else max
            sum += v
            if not stats_country.has_key(country):
                min_c = v
                sum_c = v
                max_c = v
                n_c = 1
            else:
                (min_c, sum_c, max_c, n_c) = stats_country[country]
                min_c = v if v < min_c else min_c
                max_c = v if v > max_c else max_c
                sum_c += v
                n_c += 1
            stats_country[country] = [min_c, sum_c, max_c, n_c]
        stats_analyser[analyser] = [min, sum/len(matrix[analyser]), max]
    avg_country = {}
    for country in stats_country:
        stats_country[country][1] = stats_country[country][1]/stats_country[country][3]
    keys = sorted(keys.keys())

    return template('control/updates_matrix', keys=keys, matrix=matrix, stats_analyser=stats_analyser, stats_country=stats_country)


@route('/control/update_summary')
def updates(db, lang):
    db.execute("""
SELECT
    RIGHT(MD5(remote_ip), 4) AS remote_ip,
    country,
    MAX(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp))) AS max_age,
    MIN(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp))) AS min_age,
    MAX(dynpoi_update.version) AS max_version,
    MIN(dynpoi_update.version) AS min_version,
    count(*) AS count
FROM
    source
    JOIN dynpoi_update_last ON
        source.id = dynpoi_update_last.source
    JOIN dynpoi_update ON
        dynpoi_update.source = dynpoi_update_last.source AND
        dynpoi_update.timestamp = dynpoi_update_last.timestamp
GROUP BY
    remote_ip,
    country
ORDER BY
    remote_ip,
    MIN(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp))) ASC
""")

    summary = defaultdict(list)
    max_versions = defaultdict(list)
    min_versions = defaultdict(list)
    for res in db.fetchall():
        (remote, country, max_age, min_age, max_version, min_version, count) = res
        summary[remote].append({'country': country, 'max_age': max_age/60/60/24, 'min_age': min_age/60/60/24, 'count': count})
        max_versions[remote].append(max_version)
        min_versions[remote].append(min_version)
    for remote in max_versions.keys():
        max_versions[remote] = max(max_versions[remote])
        if max_versions[remote] and '-' in max_versions[remote]:
          max_versions[remote] = '-'.join(max_versions[remote].split('-')[1:5])
        min_versions[remote] = min(min_versions[remote])
        if min_versions[remote] and '-' in min_versions[remote]:
          min_versions[remote] = '-'.join(min_versions[remote].split('-')[1:5])

    return template('control/updates_summary', summary=summary, max_versions=max_versions, min_versions=min_versions)


@route('/control/update/<source:int>')
def update(db, lang, source=None):
    sql = "SELECT source,timestamp,remote_url,remote_ip,version FROM dynpoi_update WHERE source=%d ORDER BY timestamp DESC;" % source
    db.execute(sql)
    return template('control/update', liste=db.fetchall())


@route('/control/i18n')
def update():
    return os.popen("cd po && make statistics | sed -n '1h;2,$H;${g;s/\\n/<br>/g;p}'").read()


@route('/control/lang')
def update(lang):
    out = "Accept-Language: " + request.headers['Accept-Language'] + "\n"
    if request.get_cookie('lang'):
        out += "Cookie: " + request.get_cookie('lang') + "\n"
    out += "Chosen languages: " + (",".join(lang)) + "\n"
    response.content_type = "text/plain; charset=utf-8"
    return out


@post('/control/send-update')
@post('/cgi-bin/update.py') # Backward compatibility
def send_update():
    src = request.params.get('source', default=None)
    code = request.params.get('code')
    url = request.params.get('url', default=None)
    upload = request.files.get('content', default=None)

    response.content_type = "text/plain; charset=utf-8"

    if not code or not (url or upload):
        return "FAIL"

    remote_ip = request.remote_addr

    sources = utils.get_sources()
    for s in sources:
        if src and sources[s]["comment"] != src:
            continue
        if sources[s]["password"] != code:
            continue

        try:
            if url:
                tools.update.update(sources[s], url, remote_ip=remote_ip)

            elif upload:
                (name, ext) = os.path.splitext(upload.filename)
                if ext not in ('.bz2','.gz','.xml'):
                    return 'FAIL: File extension not allowed.'

                save_filename = os.path.join(utils.dir_results, upload.filename)
                upload.save(save_filename, overwrite=True)
                tools.update.update(sources[s], save_filename, remote_ip=remote_ip)
                os.unlink(save_filename)

        except tools.update.OsmoseUpdateAlreadyDone:
            pass

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
