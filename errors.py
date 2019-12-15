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

from bottle import route, request, template, response, abort, redirect
from tools import utils
from tools import query
from tools import query_meta
from tools.OrderedDict import OrderedDict
import StringIO, re, csv

import errors_graph


def _errors_geo(db, params):
    results = query._gets(db, params)

    features = []

    for res in results:
        properties = {"error_id": res["uuid"], "item": res["item"] or 0}
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(res["lon"]), float(res["lat"])]}, "properties": properties})

    return {"type": "FeatureCollection", "features": features}


def _errors(db, lang, params):
    results = query._gets(db, params)
    out = OrderedDict()

    if not params.full:
        out["description"] = ["lat", "lon", "error_id", "item"]
    else:
        out["description"] = ["lat", "lon", "error_id", "item", "source", "class", "elems", "subclass", "subtitle", "title", "level", "update", "username"]
    out["errors"] = []

    translate = utils.translator(lang)

    for res in results:
        lat       = res["lat"]
        lon       = res["lon"]
        error_id  = res["id"]
        item      = res["item"] or 0

        if not params.full:
            out["errors"].append([str(lat), str(lon), str(error_id), str(item)])
        else:
            source    = res["source"]
            classs    = res["class"]
            elems     = '_'.join(map(lambda elem: {'N':'node', 'W':'way', 'R':'relation'}[elem['type']] + str(elem['id']), res['elems'] or []))
            subclass  = 0
            subtitle  = translate.select(res["subtitle"])
            title     = translate.select(res["title"])
            level     = res["level"]
            update    = res["timestamp"]
            username  = ','.join(map(lambda elem: "username" in elem and elem["username"] or "", res['elems'] or []))
            out["errors"].append([str(lat), str(lon), str(error_id), str(item), str(source), str(classs), str(elems), str(subclass), subtitle, title, str(level), str(update), username])

    return out


@route('/api/0.2/errors')
def errors(db, lang):
    params = query._params()
    return _errors(db, lang, params)


@route('/api/0.3beta/issues')
def errors(db, lang):
    params = query._params(max_limit=10000)
    results = query._gets(db, params)
    translate = utils.translator(lang)

    out = []
    for res in results:
        i = {
            'lat': float(res["lat"]),
            'lon': float(res["lon"]),
            'id': res["uuid"],
            'item': str(res["item"]),
        }
        if params.full:
            i.update({
                'lat': float(res["lat"]),
                'lon': float(res["lon"]),
                'id': res["uuid"],
                'item': str(res["item"]),
                'source': res["source"],
                'classs': res["class"],
                'subtitle': translate.select(res["subtitle"]),
                'title': translate.select(res["title"]),
                'level': res["level"],
                'update': str(res["timestamp"]),
                'usernames': map(lambda elem: "username" in elem and elem["username"] or "", errors['elems'] or []),
            })
        out.append(i)

    return {'issues': out}


def int_list(s):
    return map(lambda x: int(x), filter(lambda x: x and x!='',s).split(','))

@route('/errors/graph.<format:ext>')
def graph(db, format='png'):
    class options:
        sources = request.params.get('source', type=int_list, default=[])
        classes = request.params.get('class', type=int_list, default=[])
        items   = request.params.get('item', type=int_list, default=[])
        levels  = request.params.get('level', type=int_list, default=[])
        country = request.params.get('country')
        if country <> None and not re.match(r"^([a-z_]+(\*|))$", country):
            country = None

    try:
        data = errors_graph.make_plt(db, options, format)
        response.content_type = {'png':'image/png', 'svg':'image/svg+xml', 'pdf':'application/pdf'}[format]
        return data
    except Exception, e:
        response.content_type = "text/plain"
        import traceback
        out = StringIO.StringIO()
        traceback.print_exc(file=out)
        return out.getvalue() + "\n"


@route('/errors')
@route('/errors.<format:ext>')
@route('/errors/')
@route('/errors/done')
@route('/errors/done.<format:ext>')
@route('/errors/false-positive')
@route('/errors/false-positive.<format:ext>')
def index(db, lang, format=None):
    if "false-positive" in request.path:
        title = _("False positives")
        gen = "false-positive"
    elif "done" in request.path:
        title = _("Fixed issues")
        gen = "done"
    else:
        title = _("Informations")
        gen = "error"

    if not format in ('rss', 'gpx', 'kml', 'josm', 'csv'):
        format = None

    countries = query_meta._countries(db, lang) if format == None else None
    items = query_meta._items(db, lang)

    params = query._params()
    params.status = {"error":"open", "false-positive": "false", "done":"done"}[gen]
    params.limit = None
    params.fixable = None

    if format == None and params.item:
        errors_groups = query._count(db, params, [
            "dynpoi_class.item",
            "marker.source",
            "marker.class",
            "source.country",
            "source.analyser",
            "dynpoi_update_last.timestamp"], [
            "dynpoi_item",
            "class"], [
            "min(dynpoi_item.menu::text)::jsonb AS menu",
            "min(class.title::text)::jsonb AS title"],
        )

        total = 0
        for res in errors_groups:
            if res["count"] != -1:
                total += res["count"]
    else:
        errors_groups = []
        total = 0

    params.limit = request.params.get('limit', type=int, default=100)
    if params.limit > 10000:
        params.limit = 10000

    if (total > 0 and total < 1000) or params.limit:
        params.full = True
        errors = query._gets(db, params)
        if gen in ("false-positive", "done"):
            opt_date = "date"
        else:
            opt_date = "-1"
    else:
        opt_date = None
        errors = None

    if format == 'rss':
        response.content_type = 'application/rss+xml'
        tpl = 'errors/list.rss'
    elif format == 'gpx':
        response.content_type = 'application/gpx+xml'
        tpl = 'errors/list.gpx'
    elif format == 'kml':
        response.content_type = 'application/vnd.google-earth.kml+xml'
        tpl = 'errors/list.kml'
    elif format == 'josm':
        objects = set(sum(map(lambda error: map(lambda elem: elem['type'].lower() + str(elem['id']), error['elems'] or []), errors), []))
        response.status = 302
        response.set_header('Location', 'http://localhost:8111/load_object?objects=%s' % ','.join(objects))
        return
    elif format == 'csv':
        output = StringIO.StringIO()
        writer = csv.writer(output)
        h = ['uuid', 'source', 'item', 'class', 'level', 'title', 'subtitle', 'country', 'analyser', 'timestamp', 'username', 'lat', 'lon', 'elems']
        writer.writerow(h)
        for res in errors:
            usernames = map(lambda elem: elem.get("username", ""), res['elems'] or [])
            elems = '_'.join(map(lambda elem: {'N':'node', 'W':'way', 'R':'relation'}[elem['type']] + str(elem['id']), res['elems'] or []))
            writer.writerow(map(lambda a: usernames if a == 'username' else elems if a == 'elems' else res[a], h))
        response.content_type = 'text/csv'
        return output.getvalue()
    else:
        tpl = 'errors/index'

    return template(tpl, countries=countries, items=items, errors_groups=errors_groups, total=total, errors=errors, query=request.query_string, country=params.country, item=params.item, level=params.level, translate=utils.translator(lang), gen=gen, opt_date=opt_date, title=title, website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read)
