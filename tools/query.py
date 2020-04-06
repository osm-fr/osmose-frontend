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

from tools import utils, tiles


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
                    n = int(i[0])
                    where.append("(%s.item >= %s000 AND %s.item < %s000)" % (table, n, table, n + 1))
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


def _build_param(db, bbox, source, item, level, users, classs, country, useDevItem, status, tags, fixable, forceTable=[],
                 summary=False, stats=False, start_date=None, end_date=None, last_update=None, tilex=None, tiley=None, zoom=None,
                 osm_type=None, osm_id=None):
    join = ""
    where = ["1=1"]

    if summary:
        join += "dynpoi_class AS marker"
    elif stats:
        join += "stats AS marker"
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
        tables.append("class")
    if country is not None:
        tables.append("source")
    if not stats:
        tables.append("dynpoi_item")
        if useDevItem:
            tablesLeft.append("dynpoi_item")
    if last_update:
            tables.append("dynpoi_update_last")

    if "dynpoi_class" in tables:
        join += """
        JOIN dynpoi_class ON
            marker.source = dynpoi_class.source AND
            marker.class = dynpoi_class.class"""

    if "class" in tables:
        join += """
        JOIN class ON
            """ + itemField + """.item = class.item AND
            """ + itemField + """.class = class.class"""

    if "source" in tables:
        join += """
        JOIN source ON
            marker.source = source.id"""

    if "dynpoi_item" in tables:
        join += """
        %sJOIN dynpoi_item ON
            %s.item = dynpoi_item.item""" % ("LEFT " if "dynpoi_item" in tablesLeft else "", itemField)

    if "dynpoi_update_last" in tables:
        join += """
        JOIN dynpoi_update_last ON
            dynpoi_update_last.source = marker.source"""

    if item != None:
        where.append(_build_where_item(item, itemField))

    if level and level != "1,2,3":
        where.append("class.level IN (%s)" % level)

    if classs:
        where.append("marker.class IN (%s)" % ','.join(map(lambda c: str(int(c)), classs.split(','))))

    if bbox:
        where.append("marker.lat BETWEEN %f AND %f AND marker.lon BETWEEN %f AND %f" % (bbox[1], bbox[3], bbox[0], bbox[2]))
        # Compute a tile to use index
        tilex, tiley, zoom = tiles.bbox2tile(*bbox)
        if zoom < 8:
            zoom = 8
            tilex, tiley = tiles.lonlat2tile((bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2, zoom)

    if tilex and tiley and zoom:
        where.append("lonlat2z_order_curve(lon, lat) BETWEEN zoc18min(z_order_curve({x}, {y}), {z}) AND zoc18max(z_order_curve({x}, {y}), {z}) AND lat > -90".format(z=zoom, x=tilex, y=tiley))

    if country is not None:
        if len(country) >= 1 and country[-1] == "*":
            country = country[:-1] + "%"
        where.append("source.country LIKE '%s'" % country)

    if not status in ("done", "false") and useDevItem == True:
        where.append("dynpoi_item.item IS NULL")

    if not status in ("done", "false") and users:
        where.append("ARRAY['%s'] && marker_usernames(marker.elems)" % "','".join(map(lambda user: utils.pg_escape(db.mogrify(user).decode('utf-8')), users)))

    if stats:
        if start_date and end_date:
            where.append("marker.timestamp_range && tsrange('{0}', '{1}', '[]')".format(start_date.isoformat(), end_date.isoformat()))
        elif start_date:
            where.append("marker.timestamp_range && tsrange('{0}', NULL, '[)')".format(start_date.isoformat()))
        elif end_date:
            where.append("marker.timestamp_range && tsrange(NULL, '{1}', '(]')".format(end_date.isoformat()))
    elif status in ("done", "false"):
        if start_date:
            where.append("marker.date > '%s'" % start_date.isoformat())
        if end_date:
            where.append("marker.date < '%s'" % end_date.isoformat())

    if tags:
        where.append("class.tags::text[] && ARRAY['%s']" % "','".join(map(utils.pg_escape, tags)))

    if fixable == 'online':
        where.append("(SELECT bool_or(fix->'id' != '0'::jsonb) FROM (SELECT jsonb_array_elements(unnest(fixes))) AS t(fix))")
    elif fixable == 'josm':
        where.append("fixes IS NOT NULL")

    if osm_type and osm_id and join.startswith("marker"):
        where.append('ARRAY[%s::bigint] <@ marker_elem_ids(elems)' % (osm_id, )) # Match the index
        where.append('(SELECT bool_or(elem->\'type\' = \'"%s"\'::jsonb AND elem->\'id\' = \'%s\'::jsonb) FROM (SELECT unnest(elems)) AS t(elem))' % (osm_type[0].upper(), osm_id)) # Recheck with type

    return (join, " AND\n        ".join(where))


def fixes_default(fixes):
    if fixes:
        fs = list(map(lambda fix_elems: list(map(lambda fix: dict(fix,
            type=fix.get('type', 'N'),
            id=fix.get('id', 0),
            create=fix.get('create', {}),
            modify=fix.get('modify', {}),
            delete=fix.get('delete', []),
        ), fix_elems)), fixes))
        return fs


def _gets(db, params):
    sqlbase = """
    SELECT
        uuid_to_bigint(uuid) as id,
        marker.uuid AS uuid,"""
    if not params.status in ("done", "false"):
        sqlbase += """
        marker.item,
        marker.class,"""
    else:
        sqlbase += """
        dynpoi_class.item,
        dynpoi_class.class,"""
    sqlbase += """
        marker.lat,
        marker.lon,"""
    if params.full:
        sqlbase += """
        marker.source,
        marker.elems,
        marker.subtitle,
        source.country,
        source.analyser,
        class.title,
        class.level,
        dynpoi_update_last.timestamp,
        dynpoi_item.menu"""
        if not params.status in ("done", "false"):
            sqlbase += """,
        -1 AS date"""
        else:
            sqlbase += """,
        marker.date,"""
    sqlbase = sqlbase[0:-1] + """
    FROM
        %s
        JOIN dynpoi_update_last ON
            marker.source = dynpoi_update_last.source
    WHERE
        %s AND
        dynpoi_update_last.timestamp > (now() - interval '3 months')
    """
    if params.limit:
        sqlbase += """
    LIMIT
        %s""" % params.limit

    if params.full:
        forceTable = ["class", "source"]
    else:
        forceTable = []

    join, where = _build_param(db, params.bbox, params.source, params.item, params.level, params.users, params.classs, params.country, params.useDevItem, params.status, params.tags, params.fixable, forceTable=forceTable, start_date=params.start_date, end_date=params.end_date, tilex=params.tilex, tiley=params.tiley, zoom=params.zoom, osm_type=params.osm_type, osm_id=params.osm_id)
    sql = sqlbase % (join, where)
    db.execute(sql) # FIXME pas de %
    results = db.fetchall()

    for res in results:
       if 'elems' in res and res['elems']:
           res['elems'] = list(map(lambda elem: dict(elem,
               type_long={'N':'node', 'W':'way', 'R':'relation'}[elem['type']],
           ), res['elems']))

    return results


def _count(db, params, by, extraFrom=[], extraFields=[], orderBy=False):
    params.full = False

    if params.bbox or params.users or (params.status in ("done", "false")):
        summary = False
        countField = [ "count(*) AS count" ]
    else:
        summary = True
        countField = [ "SUM(marker.count) AS count" ]

    byTable = set(list(map(lambda x: x.split('.')[0], by)) + extraFrom)
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
    last_update = False
    if "dynpoi_update_last" in byTable:
        last_update = True

    join, where = _build_param(db, params.bbox, params.source, params.item, params.level, params.users, params.classs, params.country, params.useDevItem, params.status, params.tags, params.fixable, summary=summary, forceTable=byTable, start_date=params.start_date, end_date=params.end_date, last_update=last_update, tilex=params.tilex, tiley=params.tiley, zoom=params.zoom, osm_type=params.osm_type, osm_id=params.osm_id)
    sql = sqlbase % (select, join, where, groupBy, order)
    db.execute(sql) # FIXME pas de %
    results = db.fetchall()

    return results
