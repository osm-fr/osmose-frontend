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
        source.id = dynpoi_update_last.source
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
    coalesce(backend.hostname, dynpoi_update_last.remote_ip) AS remote,
    RIGHT(MD5(remote_ip), 4) AS remote_ip_hash,
    country,
    MAX(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp))) AS max_age,
    MIN(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp))) AS min_age,
    MAX(dynpoi_update_last.version) AS max_version,
    MIN(dynpoi_update_last.version) AS min_version,
    count(*) AS count
FROM
    source
    JOIN dynpoi_update_last ON
        source.id = dynpoi_update_last.source
    LEFT JOIN backend ON
        dynpoi_update_last.remote_ip = backend.ip
GROUP BY
    remote,
    remote_ip_hash,
    country
ORDER BY
    remote,
    MIN(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp))) ASC
""")

    summary = defaultdict(list)
    remote_hashes = {}
    max_versions = defaultdict(list)
    min_versions = defaultdict(list)
    for res in db.fetchall():
        (remote, remote_hash, country, max_age, min_age, max_version, min_version, count) = res
        summary[remote].append({'country': country, 'max_age': max_age/60/60/24, 'min_age': min_age/60/60/24, 'count': count})
        remote_hashes[remote] = remote_hash
        max_versions[remote].append(max_version)
        min_versions[remote].append(min_version)
    for remote in max_versions.keys():
        max_versions[remote] = max(max_versions[remote])
        if max_versions[remote] and '-' in max_versions[remote]:
          max_versions[remote] = '-'.join(max_versions[remote].split('-')[1:5])
        min_versions[remote] = min(min_versions[remote])
        if min_versions[remote] and '-' in min_versions[remote]:
          min_versions[remote] = '-'.join(min_versions[remote].split('-')[1:5])

    return template('control/updates_summary', summary=summary, max_versions=max_versions, min_versions=min_versions, remote_hashes=remote_hashes)


@route('/control/update_summary_by_analyser')
def updates(db, lang):
    db.execute("""
SELECT
    analyser,
    COUNT(*),
    MIN(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp)))/60/60/24 AS min_age,
    MAX(EXTRACT(EPOCH FROM ((now())-dynpoi_update_last.timestamp)))/60/60/24 AS max_age,
    MIN(dynpoi_update_last.version) AS min_version,
    MAX(dynpoi_update_last.version) AS max_version
FROM
    source
    JOIN dynpoi_update_last ON
        source.id = dynpoi_update_last.source
WHERE
    dynpoi_update_last.version IS NOT NULL AND
    dynpoi_update_last.version NOT IN ('(None)', '(unknown)')
GROUP BY
    analyser
ORDER BY
    analyser
""")

    summary = defaultdict(list)
    max_versions = None
    for res in db.fetchall():
        (analyser, count, min_age, max_age, min_version, max_version) = res
        max_versions = max_version if max_version > max_versions else max_versions
        summary[analyser] = {'count': count, 'min_age': min_age, 'max_age': max_age, 'max_version': '-'.join((max_version or '').split('-')[1:5]), 'min_version': '-'.join((min_version or '').split('-')[1:5])}

    max_versions = '-'.join((max_versions or '').split('-')[1:5])

    return template('control/updates_summary_by_analyser', summary=summary, max_versions=max_versions)


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
def send_update(db):
    src = request.params.get('source', default=None)
    code = request.params.get('code')
    upload = request.files.get('content', default=None)

    response.content_type = "text/plain; charset=utf-8"

    if not code or not upload:
        return "FAIL"

    db.execute("""
SELECT
    id
FROM
    source
    JOIN source_password ON
        source.id = source_id
WHERE
    analyser || '-' || country = %(comment)s AND
    password = %(password)s
LIMIT 1
""", {"comment": src, "password": code})

    res = db.fetchone()

    if not res and not os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        return "AUTH FAIL"
    if not res and os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        r = db.execute("SELECT COALESCE(MAX(id), 0) + 1 AS id FROM source")
        source_id = db.fetchone()["id"]
        analyser, country = src.split("-")
        db.execute("INSERT INTO source(id, country, analyser) VALUES (%s, %s, %s)", (source_id, country, analyser))
        db.execute("INSERT INTO source_password(source_id, password) VALUES(%s, %s)", (source_id, code))
        db.connection.commit()
    else:
        source_id = res["id"]

    remote_ip = request.remote_addr

    try:
        (name, ext) = os.path.splitext(upload.filename)
        if ext not in ('.bz2','.gz','.xml'):
            return 'FAIL: File extension not allowed.'

        save_filename = os.path.join(utils.dir_results, upload.filename)
        upload.save(save_filename, overwrite=True)
        tools.update.update(source_id, save_filename, remote_ip=remote_ip)
        os.unlink(save_filename)

    except tools.update.OsmoseUpdateAlreadyDone:
        return 'FAIL: Already up to date'

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

@route('/control/status/<country>/<analyser>')
def status(db, country = None, analyser = None):
    if not country or not analyser:
        return "FAIL"

    response.content_type = 'text/plain; charset=utf-8'

    ret = ''
    db.execute('SELECT timestamp, source, analyser_version FROM dynpoi_update_last WHERE source = (SELECT id FROM source WHERE analyser = %s AND country = %s)', (analyser, country))
    r = db.fetchone()
    if r and r['timestamp']:
        ret + "1\n" # status format version
        ret += str(r['timestamp']) + "\n"
        ret += str(r["analyser_version"] or "") + "\n"
        for t in ['N', 'W', 'R']:
            db.execute('SELECT string_agg(id::text, \',\') FROM (SELECT DISTINCT marker_elem.id AS id FROM marker JOIN marker_elem ON marker_elem.marker_id = marker.id WHERE source=%s AND data_type = %s) AS t', (r['source'], t))
            s = db.fetchone()
            if s and s[0]:
                ret += s[0]
            ret += "\n"
        return ret

    return 'NOTHING'
