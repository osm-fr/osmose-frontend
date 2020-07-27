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

from bottle import route, request, template
from .tool.translation import translator
from collections import defaultdict


@route('/control/update')
def updates(db, lang):
    db.execute("""
SELECT
    sources.id,
    EXTRACT(EPOCH FROM ((now())-updates_last.timestamp)) AS age,
    sources.country,
    sources.analyser
FROM
    sources
    LEFT JOIN updates_last ON
        sources.id = updates_last.source_id
ORDER BY
    updates_last.timestamp DESC
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
    liste.sort(key = lambda a: a[2])

    return template('control/updates', translate=translator(lang), liste=liste)


@route('/control/update_matrix')
def updates(db, lang):
    remote = request.params.get('remote')
    country = request.params.get('country')
    db.execute("""
SELECT DISTINCT ON (sources.id)
    sources.id,
    EXTRACT(EPOCH FROM ((now())-updates_last.timestamp)) AS age,
    country,
    analyser
FROM
    sources
    JOIN updates_last ON
        sources.id = updates_last.source_id
WHERE
""" + ("""
    RIGHT(MD5(remote_ip), 4) = %(remote)s AND """ if remote else "") + ("""
    sources.country LIKE %(country)s AND """ if country else "") + """
    true
ORDER BY
    sources.id ASC,
    updates_last.timestamp DESC
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
            if country not in stats_country:
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

    return template('control/updates_matrix', translate=translator(lang), keys=keys, matrix=matrix, stats_analyser=stats_analyser, stats_country=stats_country)


@route('/control/update_summary')
def updates(db, lang):
    db.execute("""
SELECT
    backend.hostname AS hostname,
    updates_last.remote_ip AS remote,
    RIGHT(MD5(remote_ip), 4) AS remote_ip_hash,
    country,
    MAX(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp))) AS max_age,
    MIN(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp))) AS min_age,
    MAX(updates_last.version) AS max_version,
    MIN(updates_last.version) AS min_version,
    count(*) AS count
FROM
    sources
    JOIN updates_last ON
        sources.id = updates_last.source_id
    LEFT JOIN backend ON
        updates_last.remote_ip = backend.ip
GROUP BY
    hostname,
    remote_ip,
    remote_ip_hash,
    country
ORDER BY
    min_age ASC
""")

    summary = defaultdict(list)
    remote_hashes = {}
    hostnames = defaultdict(list)
    max_versions = defaultdict(list)
    min_versions = defaultdict(list)
    max_count = 0
    for res in db.fetchall():
        (hostname, remote, remote_hash, country, max_age, min_age, max_version, min_version, count) = res
        max_count = max(max_count, count)
        summary[remote].append({'hostname': hostname, 'country': country, 'max_age': max_age/60/60/24, 'min_age': min_age/60/60/24, 'count': count})
        remote_hashes[remote] = remote_hash
        hostnames[remote].append(hostname)
        max_versions[remote].append(max_version)
        min_versions[remote].append(min_version)
    for remote in max_versions.keys():
        hostnames[remote] = hostnames[remote][0]
        max_versions[remote] = max(max_versions[remote])
        if max_versions[remote] and '-' in max_versions[remote]:
          max_versions[remote] = '-'.join(max_versions[remote].split('-')[1:5])
        min_versions[remote] = min(min_versions[remote])
        if min_versions[remote] and '-' in min_versions[remote]:
          min_versions[remote] = '-'.join(min_versions[remote].split('-')[1:5])

    return template('control/updates_summary', translate=translator(lang), summary=summary, hostnames=hostnames, max_versions=max_versions, min_versions=min_versions, remote_hashes=remote_hashes, max_count=max_count)


@route('/control/update_summary_by_analyser')
def updates(db, lang):
    db.execute("""
SELECT
    analyser,
    COUNT(*),
    MIN(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp)))/60/60/24 AS min_age,
    MAX(EXTRACT(EPOCH FROM ((now())-updates_last.timestamp)))/60/60/24 AS max_age,
    MIN(updates_last.version) AS min_version,
    MAX(updates_last.version) AS max_version
FROM
    sources
    JOIN updates_last ON
        sources.id = updates_last.source_id
WHERE
    updates_last.version IS NOT NULL AND
    updates_last.version NOT IN ('(None)', '(unknown)')
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

    return template('control/updates_summary_by_analyser', translate=translator(lang), summary=summary, max_versions=max_versions)


@route('/control/update/<source:int>')
def update(db, lang, source=None):
    sql = "SELECT source_id,timestamp,remote_url,remote_ip,version FROM updates WHERE source_id=%d ORDER BY timestamp DESC;" % source
    db.execute(sql)
    return template('control/update', translate=translator(lang), liste=db.fetchall())
