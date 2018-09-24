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

from bottle import route, request, template, response, redirect, abort, static_file, HTTPError
from tools import utils, query, query_meta, tiles
import urllib
import byuser
import errors
import datetime
import math, StringIO
from shapely.geometry import Point, Polygon
import mapbox_vector_tile


def check_items(items, all_items):
    if items == None or items == 'xxxx':
        return all_items
    else:
        items = items.split(',')
        it = filter(lambda i: str(i)[0]+'xxx' in items, all_items)
        for i in items:
            try:
                n = int(i)
                it.append(n)
            except:
                pass
        return it


@route('/map')
def index_redirect():
    new_url = "map/"
    if request.query_string:
        new_url += "#" + request.query_string
    redirect(new_url)

@route('/map/')
def index(db, lang):
    if request.query_string:
        redirect("./#" + request.query_string)

    tags = query_meta._tags(db, lang)

    db.execute("SELECT item FROM dynpoi_item GROUP BY item;")
    all_items = map(lambda res: int(res[0]), db.fetchall())

    categories = query_meta._categories(db, lang)

    item_tags = {}
    item_levels = {"1": set(), "2": set(), "3": set()}
    for categ in categories:
        for err in categ["item"]:
            for l in err["levels"]:
                item_levels[str(l)].add(err["item"])
            if err["tags"]:
                for t in err["tags"]:
                    if not item_tags.has_key(t):
                        item_tags[t] = set()
                    item_tags[t].add(err["item"])

    item_levels["1,2"] = item_levels["1"] | item_levels["2"]
    item_levels["1,2,3"] = item_levels["1,2"] | item_levels["3"]

    urls = []
    # TRANSLATORS: link to help in appropriate language
    urls.append(("byuser", _("Issues by user"), "../byuser/"))
    urls.append(("relation_analyser", _("Relation analyser"), "http://analyser.openstreetmap.fr/"))
    # TRANSLATORS: link to source code
    urls.append(("statistics", _("Statistics"), "../control/update_matrix"))

    helps = []
    helps.append((_("Contact"), "../contact"))
    helps.append((_("Help on wiki"), _("http://wiki.openstreetmap.org/wiki/Osmose")))
    helps.append((_("Copyright"), "../copyright"))
    helps.append((_("Sources"), "https://github.com/osm-fr?q=osmose"))
    helps.append((_("Translation"), "../translation"))

    sql = """
SELECT
    EXTRACT(EPOCH FROM ((now())-timestamp)) AS age
FROM
    dynpoi_update_last
ORDER BY
    timestamp
LIMIT
    1
OFFSET
    (SELECT COUNT(*)/2 FROM dynpoi_update_last)
;
"""
    db.execute(sql)
    delay = db.fetchone()
    if delay and delay[0]:
        delay = delay[0]/60/60/24
    else:
        delay = 0

    if request.session.has_key('user'):
        if request.session['user']:
            user = request.session['user']['osm']['user']['@display_name']
            user_error_count = byuser._user_count(db, user.encode('utf-8'))
        else:
            user = '[user name]'
            user_error_count = {1: 0, 2: 0, 3: 0}
    else:
        user = None
        user_error_count = None

    return template('map/index', categories=categories, item_tags=item_tags, tags=tags, item_levels=item_levels,
        main_project=utils.main_project, urls=urls, helps=helps, delay=delay, languages_name=utils.languages_name, translate=utils.translator(lang),
        website=utils.website, remote_url_read=utils.remote_url_read, request=request,
        user=user, user_error_count=user_error_count)


def _errors_mvt(db, params, z, min_lon, min_lat, max_lon, max_lat, limit):
    params.limit = limit
    results = query._gets(db, params) if z >= 6 else None

    if not results or len(results) == 0:
        return None
    else:
        limit_feature = []
        if len(results) == limit and z < 18:
            limit_feature = [{
                "name": "limit",
                "features": [{
                    "geometry": Point((min_lon + max_lon) / 2, (min_lat + max_lat) / 2)
                }]
            }]

        issues_features = []
        for res in sorted(results, key=lambda res: -res["lat"]):
            issues_features.append({
                "geometry": Point(res["lon"], res["lat"]),
                "properties": {
                    "issue_id": res["id"],
                    "item": res["item"] or 0,
                    "class": res["class"] or 0}
            })

        return mapbox_vector_tile.encode([{
            "name": "issues",
            "features": issues_features
        }] + limit_feature, quantize_bounds=(min_lon, min_lat, max_lon, max_lat))


@route('/map/heat/<z:int>/<x:int>/<y:int>.mvt')
def heat(db, z, x, y):
    COUNT=32

    lon1,lat2 = tiles.tile2lonlat(x,y,z)
    lon2,lat1 = tiles.tile2lonlat(x+1,y+1,z)

    params = query._params()
    items = query._build_where_item(params.item, "dynpoi_item")
    params.tilex = x
    params.tiley = y
    params.zoom = z

    if params.zoom > 18:
        return

    db.execute("""
SELECT
    SUM((SELECT SUM(t) FROM UNNEST(number) t))
FROM
    dynpoi_item
WHERE
""" + items)
    limit = db.fetchone()
    if limit and limit[0]:
        limit = float(limit[0])
    else:
        return HTTPError(404)

    join, where = query._build_param(None, params.source, params.item, params.level, params.users, params.classs, params.country, params.useDevItem, params.status, params.tags, params.fixable, tilex=params.tilex, tiley=params.tiley, zoom=params.zoom)
    join = join.replace("%", "%%")
    where = where.replace("%", "%%")

    sql = """
SELECT
    COUNT(*),
    ((lon-%(lon1)s) * %(count)s / (%(lon2)s-%(lon1)s) + 0.5)::int AS latn,
    ((lat-%(lat1)s) * %(count)s / (%(lat2)s-%(lat1)s) + 0.5)::int AS lonn,
    mode() WITHIN GROUP (ORDER BY dynpoi_item.marker_color) AS color
FROM
""" + join + """
WHERE
""" + where + """
GROUP BY
    latn,
    lonn
"""
    db.execute(sql, {"lon1":lon1, "lat1":lat1, "lon2":lon2, "lat2":lat2, "count":COUNT})

    features = []
    for row in db.fetchall():
        count, x, y, color = row
        count = max(
          int(math.log(count) / math.log(limit / ((z-4+1+math.sqrt(COUNT))**2)) * 255),
          1 if count > 0 else 0
        )
        if count > 0:
          count = 255 if count > 255 else count
          features.append({
            "geometry": Polygon([(x, y), (x - 1, y), (x - 1, y - 1), (x, y - 1)]),
            "properties": {
                "color": int(color[1:], 16),
                "count": count}
          })

    response.content_type = 'application/vnd.mapbox-vector-tile'
    return mapbox_vector_tile.encode([{
        "name": "issues",
        "features": features
    }], extents=COUNT)


@route('/map/issues/<z:int>/<x:int>/<y:int>.mvt')
def issues_mvt(db, z, x, y):
    lon1,lat2 = tiles.tile2lonlat(x,y,z)
    lon2,lat1 = tiles.tile2lonlat(x+1,y+1,z)
    dlon = (lon2 - lon1) / 256
    dlat = (lat2 - lat1) / 256

    params = query._params()
    params.tilex = x
    params.tiley = y
    params.zoom = z

    if params.zoom > 18:
        return
    if (not params.users) and (not params.source) and (params.zoom < 6):
        return

    params.limit = 50
    params.full = False

    tile = _errors_mvt(db, params, z, lon1, lat1, lon2, lat2, 50)
    if tile:
        response.content_type = 'application/vnd.mapbox-vector-tile'
        return tile
    else:
        return HTTPError(404)


@route('/map/markers')
def markers(db):
    params = query._params()

    if (not params.users) and (not params.source) and (params.zoom < 6):
        return

    params.limit = 200
    params.full = False

    return errors._errors_geo(db, params)


@route('/tpl/popup.tpl')
def popup_template(lang):
    return template('map/popup', mustache_delimiter="{{={% %}=}}", website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read)

@route('/tpl/editor.tpl')
def editor_template(lang):
    return template('map/editor', mustache_delimiter="{{={% %}=}}", main_website=utils.main_website)
