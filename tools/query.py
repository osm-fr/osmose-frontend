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

from bottle import route, request, response
from tools import utils
import datetime, re


def _build_where_item(item, table):
    if item == '':
        where = "1=2"
    elif item == None or item == 'xxxx':
        where = "1=1"
    else:
        where = []
        l = []
        for i in item.split(','):
            try:
                if 'xxx' in i:
                    where.append("%s.item/1000 = %s" % (table, int(i[0])))
                else:
                    l.append(str(int(i)))
            except:
                pass
        if l != []:
            where.append("%s.item IN (%s)" % (table, ','.join(l)))
        if where != []:
            where = "(%s)" % ' OR '.join(where)
        else:
            where = "1=1"
    return where


def _build_param(lat, lon, bbox, source, item, level, users, classs, country, useDevItem, status, tags, fixable, forceTable=[],
                 summary=False, stats=False, start_date=None, end_date=None):
    join = ""
    where = ["1=1"]

    if summary:
        join += "dynpoi_class AS marker"
    elif stats:
        join += "dynpoi_stats AS marker"
    elif status in ("done", "false"):
        join += "dynpoi_status AS marker"
        where.append("marker.status = '%s'" % status)
    else:
        join += "marker"

    if source:
        sources = source.split(",")
        source2 = []
        for source in sources:
            source = source.split("-")
            if len(source)==1:
                source2.append("(marker.source=%d)"%int(source[0]))
            else:
                source2.append("(marker.source=%d AND marker.class=%d)"%(int(source[0]), int(source[1])))
        sources2 = " OR ".join(source2)
        where.append("(%s)" % sources2)

    tables = list(forceTable)
    tablesLeft = []

    if join.startswith("marker"):
        itemField = "marker"
    else:
        if item:
            tables.append("dynpoi_class")
        itemField = "dynpoi_class"
    if (level and level != "1,2,3") or tags:
        tables.append("dynpoi_class")
    if country:
        tables.append("source")
    if not stats:
        tables.append("dynpoi_item")
        if useDevItem:
            tablesLeft.append("dynpoi_item")
        if users:
            tables.append("marker_elem")

    if "dynpoi_class" in tables or "source" in tables:
        join += """
        JOIN dynpoi_class ON
            marker.source = dynpoi_class.source AND
            marker.class = dynpoi_class.class"""

    if "source" in tables:
        join += """
        JOIN source ON
            dynpoi_class.source = source.id"""

    if "dynpoi_item" in tables:
        join += """
        %sJOIN dynpoi_item ON
            %s.item = dynpoi_item.item""" % ("LEFT " if "dynpoi_item" in tablesLeft else "", itemField)

    if "marker_elem" in tables:
        join += """
        LEFT JOIN marker_elem ON
            marker_elem.marker_id = marker.id"""

    if item != None:
        where.append(_build_where_item(item, itemField))

    if level != "1,2,3":
        where.append("dynpoi_class.level IN (%s)" % level)

    if classs:
        where.append("marker.class IN (%s)" % ','.join(map(lambda c: str(int(c)), classs.split(','))))

    if lat and lon and bbox:
        where.append('point(marker.lat, marker.lon) <-> point(%f, %f) < point(%f, %f) <-> point(%f, %f)' % (lat, lon, lat, lon, bbox[1], bbox[0]))

    if bbox:
        where.append("box(point(%f, %f), point(%f, %f)) @> point(marker.lat, marker.lon)" % (bbox[1], bbox[0], bbox[3], bbox[2]))

    if country:
        if country[-1] == "*":
            country = country[:-1] + "%"
        where.append("source.country LIKE '%s'" % country)

    if not status in ("done", "false") and useDevItem == True:
        where.append("dynpoi_item.item IS NULL")

    if not status in ("done", "false") and users:
        where.append("marker_elem.username IN ('%s')" % "','".join(users))

    if stats:
        if start_date:
            where.append("marker.timestamp > '%s'" % start_date.isoformat())
        if end_date:
            where.append("marker.timestamp < '%s'" % end_date.isoformat())
    elif status in ("done", "false"):
        if start_date:
            where.append("marker.date > '%s'" % start_date.isoformat())
        if end_date:
            where.append("marker.date < '%s'" % end_date.isoformat())

    if tags:
        where.append("dynpoi_class.tags::text[] && ARRAY['%s']" % "','".join(map(utils.pg_escape, tags)))

    if fixable == 'online':
        where.append("EXISTS (SELECT 1 FROM marker_fix WHERE marker_fix.marker_id = marker.id AND elem_id != 0)")
    elif fixable == 'josm':
        where.append("EXISTS (SELECT 1 FROM marker_fix WHERE marker_fix.marker_id = marker.id)")

    return (join, " AND\n        ".join(where))


def _params():
    class Params:
        lat      = request.params.get('lat', type=float, default=0)
        lon      = request.params.get('lon', type=float, default=0)
        bbox     = request.params.get('bbox', default=None)
        item     = request.params.get('item')
        source   = request.params.get('source', default='')
        classs   = request.params.get('class', default='')
        users    = utils.pg_escape(request.params.get('username', default='').decode('utf-8'))
        level    = request.params.get('level', default='1,2,3')
        full     = request.params.get('full', default=False)
        zoom     = request.params.get('zoom', type=int, default=10)
        limit    = request.params.get('limit', type=int, default=100)
        country  = request.params.get('country', default=None)
        useDevItem= request.params.get('useDevItem', default=False)
        status   = request.params.get('status', default="open")
        start_date = request.params.get('start_date', default=None)
        end_date = request.params.get('end_date', default=None)
        tags     = request.params.get('tags', default=None)
        fixable  = request.params.get('fixable', default=None)

    params = Params()

    if params.level:
        params.level = params.level.split(",")
        try:
            params.level = ",".join([str(int(x)) for x in params.level if x])
        except:
            params.level = "1,2,3"
    if params.bbox:
        try:
            params.bbox = map(lambda x: float(x), params.bbox.split(','))
            if not params.lat or params.lat==0:
                params.lat = (params.bbox[1] + params.bbox[3]) / 2
            if not params.lon or params.lon==0:
                params.lon = (params.bbox[0] + params.bbox[2]) / 2
        except:
            params.bbox = None
    if params.users:
        params.users = params.users.split(",")
    if params.limit > 500:
        params.limit = 500
    if params.country and not re.match(r"^([a-z_]+)(\*|)$", params.country):
        params.country = None
    if params.useDevItem == "true":
        params.useDevItem = True
    elif params.useDevItem == "all":
        pass
    else:
        params.useDevItem = False
    if params.start_date:
        params.start_date = utils.str_to_datetime(params.start_date)
    if params.end_date:
        params.end_date = utils.str_to_datetime(params.end_date)
    if params.tags:
        params.tags = params.tags.split(",")

    return params


def _gets(db, params):
    sqlbase = """
    SELECT
        marker.id AS id,"""
    if not params.status in ("done", "false"):
        sqlbase += """
        marker.item,"""
    elif params.full:
        sqlbase += """
        dynpoi_class.item,"""
    else:
        sqlbase += """
        dynpoi_class.item,"""
    sqlbase += """
        marker.lat,
        marker.lon"""
    if params.full:
        sqlbase += """,
        marker.source,
        marker.class,
        marker.elems,
        marker.subclass,
        marker.subtitle,
        source.country,
        source.analyser,
        dynpoi_class.title,
        dynpoi_class.level,
        dynpoi_update_last.timestamp,
        dynpoi_item.menu"""
        if not params.status in ("done", "false"):
            sqlbase += """,
        marker_elem.username,
        -1 AS date"""
        else:
            sqlbase += """,
        '' AS username,
        marker.date"""
    sqlbase += """
    FROM
        %s
        JOIN dynpoi_update_last ON
            marker.source = dynpoi_update_last.source
    WHERE
        %s AND
        dynpoi_update_last.timestamp > (now() - interval '3 months')
    """
    if params.lat and params.lon:
        sqlbase += """
    ORDER BY
        point(marker.lat, marker.lon) <-> point(%f, %f)""" % (params.lat, params.lon)
    if params.limit:
        sqlbase += """
    LIMIT
        %s""" % params.limit

    if params.full:
        if not params.status in ("done", "false"):
            forceTable = ["dynpoi_class", "source", "marker_elem"]
        else:
            forceTable = ["dynpoi_class", "source"]
    else:
        forceTable = []

    join, where = _build_param(params.lat, params.lon, params.bbox, params.source, params.item, params.level, params.users, params.classs, params.country, params.useDevItem, params.status, params.tags, params.fixable, forceTable=forceTable, start_date=params.start_date, end_date=params.end_date)
    sql = sqlbase % (join, where)
    db.execute(sql) # FIXME pas de %
    results = db.fetchall()

    return results


def _count(db, params, by, extraFrom=[], extraFields=[], orderBy=False):
    params.full = False

    if params.bbox or params.users or (params.status in ("done", "false")):
        summary = False
        countField = [ "count(*) AS count" ]
    else:
        summary = True
        countField = [ "SUM(marker.count) AS count" ]

    byTable = set(map(lambda x: x.split('.')[0], by) + extraFrom)
    sqlbase  = """
    SELECT
        %s
    FROM
        %s
    WHERE
        %s
    GROUP BY
        %s
    ORDER BY
        %s
    """

    select = ",\n        ".join(by+extraFields+countField)
    groupBy = ",\n        ".join(by)
    if orderBy:
        order = groupBy
    else:
        order = "count DESC"
    if params.limit:
        sqlbase += " LIMIT %s" % params.limit

    join, where = _build_param(params.lat, params.lon, params.bbox, params.source, params.item, params.level, params.users, params.classs, params.country, params.useDevItem, params.status, params.tags, params.fixable, summary=summary, forceTable=byTable, start_date=params.start_date, end_date=params.end_date)
    sql = sqlbase % (select, join, where, groupBy, order)
    db.execute(sql) # FIXME pas de %
    results = db.fetchall()

    return results
