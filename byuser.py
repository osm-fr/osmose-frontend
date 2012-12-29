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

from bottle import route, request, template, redirect, response
from tools import utils


@route('/byuser')
def byUser():
    redirect("byuser/")


@route('/byuser/')
@route('/byuser/<username>')
@route('/byuser/<username>.<format:ext>')
def byUser(db, lang, username=None, format=None):
    username = username or request.params.username
    item = request.params.get('item', type=int)
    if not username:
        return template('byuser/index')
    else:
        params = [username]
        sql = """
SELECT
    m.id,
    m.class,
    m.subtitle,
    m.lat,
    m.lon,
    m.source,
    m.item,
    c.title,
    c.level,
    dynpoi_update_last.timestamp
FROM
    marker m
    JOIN dynpoi_class c ON
        m.class = c.class AND
        m.source = c.source
    JOIN dynpoi_update_last ON
        m.source = dynpoi_update_last.source
    JOIN dynpoi_item ON
        m.item = dynpoi_item.item
WHERE
    id IN (SELECT marker_id FROM marker_elem WHERE username=%s)
"""
        if item:
            sql += "AND m.item = %s "
            params.append(item)
        sql += """
ORDER BY
    dynpoi_update_last.timestamp DESC
LIMIT 500
"""

        db.execute(sql, params)
        results = db.fetchall()
        count = len(results)
        if format == 'rss':
            response.content_type = "application/rss+xml"
            return template('byuser/byuser.rss', username=username, count=count, results=results, translate=utils.translator(lang))
        else:
            return template('byuser/byuser', username=username, count=count, results=results, translate=utils.translator(lang))


@route('/byuser-stats')
def byuser_stats(db):
    sql = """
SELECT
    count(*) AS cpt,
    username
FROM
    marker_elem
GROUP BY
    username
ORDER BY
    cpt DESC
LIMIT 500
"""
    db.execute(sql)
    return template('byuser/byuser-stats', results=db.fetchall())
