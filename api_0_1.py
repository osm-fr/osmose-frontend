#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2009 Christoph Böhme, Mitja Kleider - part of Openstreetbugs.
# Copyright 2011-2012 Jocelyn Jaubert
# Copyright 2012 Frederic Rodrigo
#
# Openstreetbugs is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Openstreetbugs is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openstreetbugs. If not, see <http://www.gnu.org/licenses/>.
#

from bottle import route, response, request
from tools import utils, osmose_common


@route('/api/0.1/closePOIexec', method=['GET', 'POST'])
@route('/api/0.1.1/closePOIexec/<id:int>')
def closePOIexec(id = None):
    response.content_type = 'text/plain; Charset=UTF-8'
    id = id or request.params.get('id', type=int)
    if not id:
        return "FAIL"
    elif osmose_common.remove_bug(id, "done") == 0:
        return "OK"
    else:
        return "FAIL"


def bboxRequest2Clause():
    minlat = request.params.get("b", type=float, default=-90) * 1000000
    maxlat = request.params.get("t", type=float, default=90) * 1000000
    minlon = request.params.get("l", type=float, default=-180) * 1000000
    maxlon = request.params.get("r", type=float, default=180) * 1000000
    lat = int((minlat + maxlat) / 2)
    lon = int((minlon + maxlon) / 2)
    clause = []
    clause.append("marker.lat BETWEEN %s AND %s" % (int(minlat), int(maxlat)))
    clause.append("marker.lon BETWEEN %s AND %s" % (int(minlon), int(maxlon)))
    order = "ABS(lat - %s) + ABS(lon - %s) ASC" % (lat, lon)
    return [clause, order]

def list2Clause(l, clause, item):
    if not l:
        return
    err_id = l.split(",")
    err_id = ",".join([str(int(x)) for x in err_id if x])
    if err_id:
        clause.append("%s IN (%s)" % (item, err_id))

def query(db, sql, args, callback):
    db.execute(sql, args)
    res = db.fetchone()
    content = ''
    while res:
        content += callback(res)
        res = db.fetchone()

    return content


@route('/api/0.1/getBugs')
def getBugs(db, lang):
    clause, order = bboxRequest2Clause()
    list2Clause(request.params.get('item'), clause, 'marker.item')

    sqlbase  = """
SELECT marker.id,
    marker.item,
    marker.lat,
    marker.lon,
    dynpoi_class.title as title,
    marker.subtitle as subtitle
FROM marker
INNER JOIN dynpoi_class ON
    marker.source=dynpoi_class.source AND
    marker.class=dynpoi_class.class
INNER JOIN dynpoi_update_last ON
    marker.source = dynpoi_update_last.source
WHERE
    %s AND
    dynpoi_update_last.timestamp > (now() - interval '3 months')
ORDER BY
    %s
LIMIT 100
"""

    translate = utils.translator(lang)

    def each(res):
        lat       = float(res["lat"]) / 1000000
        lon       = float(res["lon"]) / 1000000
        error_id  = res["id"]
        title     = translate.select(res["title"])
        subtitle  = translate.select(res["subtitle"])
        item      = res["item"] or 0

        text      = title
        if subtitle:
            text += " - <br>" + subtitle
        return u"putAJAXMarker('%s', %f, %f, '%s', '%s');\n" % (error_id, lon, lat, text, item)

    response.content_type = 'text/plain; Charset=UTF-8'
    return query(db, sqlbase % (' AND '.join(clause), order), None, each)


@route('/api/0.1/getBugsByUser')
@route('/api/0.1.1/getBugs/<user>')
def getBugsByUser(db, lang, user=None):
    user = user or request.params.get('user')
    clause, order = bboxRequest2Clause()
    sql_arg = {}
    limit = ''
    if user:
        clause.append("u.username = %(username)s")
        sql_arg['username'] = user
    else:
        num_points = request.params.get('points', type=int, default=100)
        if num_points != "all":
            limit = "LIMIT %d" % int(num_points)
    list2Clause(request.params.get('class'), clause, 'm.class')
    list2Clause(request.params.item, clause, 'm.item')
    list2Clause(request.params.not_item, clause, 'm.item NOT')

    sqlbase  = """
SELECT marker.id,
       marker.item,
       marker.source,
       marker.class,
       marker.elems,
       marker.subclass,
       marker.lat,
       marker.lon,
       dynpoi_class.title as title,
       marker.subtitle as subtitle,
       dynpoi_update_last.timestamp,
       u.username
FROM marker
INNER JOIN dynpoi_class ON
    marker.source=dynpoi_class.source AND
    marker.class=dynpoi_class.class
INNER JOIN dynpoi_update_last ON
    marker.source = dynpoi_update_last.source
LEFT JOIN marker_elem u ON
    marker.id = u.marker_id
WHERE
    %s
ORDER BY
    dynpoi_update_last.timestamp DESC
%s
"""

    translate = utils.translator(lang)

    def each(res):
        lat       = float(res["lat"]) / 1000000
        lon       = float(res["lon"]) / 1000000
        error_id  = res["id"]
        title     = translate.select(res["title"])
        subtitle  = translate.select(res["subtitle"])
        item      = res["item"] or 0
        return u'"%s", "%s", "%s", %f, %f, "%s", "%s", "%s"\n' % (res["timestamp"], res["username"].decode('utf-8'), error_id, lon, lat, title, subtitle, item)

    response.content_type = 'text/plain; Charset=UTF-8'
    content = "# timestamp, username, error_id, lon, lat, title, subtitle, item\n"
    return content + query(db, sqlbase % (' AND '.join(clause), limit), sql_arg, each)


@route('/api/0.1/getUsers')
def getUsers(db):
    user = request.params.get('user')
    clause, order = bboxRequest2Clause()
    sql_arg = {}
    if user:
        clause.append("u.username = %(username)s")
        sql_arg['username'] = user

    list2Clause(request.params.get('item'), clause, 'm.item')
    list2Clause(request.params.get('not_item'), clause, 'm.item NOT')

    sqlbase  = """
SELECT
    u.username,
    count(*) AS count
FROM marker_elem u
JOIN marker ON
    marker.id = u.marker_id
WHERE
    %s
GROUP BY
    u.username
ORDER BY
    u.username
"""

    response.content_type = 'text/plain; Charset=UTF-8'
    content = "# username, count\n"
    content += query(db, sqlbase % ' AND '.join(clause), sql_arg, lambda res:
        '"%s", %d"\n' % (res["username"], int(res["count"]))
    )
    return content
