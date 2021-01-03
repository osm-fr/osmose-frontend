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

from bottle import route, request, template, response
from modules import utils
from .tool.translation import translator
from modules.params import Params
from modules import query
from modules import query_meta
from collections import defaultdict
import io, re, csv

from . import errors_graph


def int_list(s):
    return list(map(lambda x: int(x), filter(lambda x: x and x!='',s)).split(','))

@route('/errors/graph.<format:ext>')
def graph(db, format='png'):
    try:
        data = errors_graph.make_plt(db, Params(), format)
        response.content_type = {'png':'image/png', 'svg':'image/svg+xml', 'pdf':'application/pdf', 'csv':'text/csv', 'json':'application/json'}[format]
        return data
    except Exception as e:
        response.content_type = "text/plain"
        import traceback
        out = io.StringIO()
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
        title = _("Information")
        gen = "error"

    if not format in ('rss', 'gpx', 'kml', 'josm', 'csv'):
        format = None

    countries = query_meta._countries(db) if format == None else None
    items = query_meta._items_menu(db, lang)

    params = Params()
    params.status = {"error":"open", "false-positive": "false", "done":"done"}[gen]
    params.limit = None
    params.fixable = None

    if format == None and params.item:
        errors_groups = query._count(db, params, [
            "markers_counts.item",
            "markers.source_id",
            "markers.class",
            "sources.country",
            "sources.analyser",
            "updates_last.timestamp"], [
            "items",
            "class"], [
            "min(items.menu::text)::jsonb AS menu",
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
        objects = set(sum(map(lambda error: list(map(lambda elem: elem['type'].lower() + str(elem['id']), error['elems'] or [])), errors), []))
        response.status = 302
        response.set_header('Location', 'http://localhost:8111/load_object?objects=%s' % ','.join(objects))
        return
    elif format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        h = ['uuid', 'source', 'item', 'class', 'level', 'title', 'subtitle', 'country', 'analyser', 'timestamp', 'username', 'lat', 'lon', 'elems']
        writer.writerow(h)
        for res in errors:
            usernames = list(map(lambda elem: elem.get("username", ""), res['elems'] or []))
            elems = '_'.join(map(lambda elem: {'N':'node', 'W':'way', 'R':'relation'}[elem['type']] + str(elem['id']), res['elems'] or []))
            writer.writerow(list(map(lambda a: usernames if a == 'username' else elems if a == 'elems' else res[a], h)))
        response.content_type = 'text/csv'
        return output.getvalue()
    else:
        tpl = 'errors/index'

    return template(tpl, countries=countries, items=items, errors_groups=errors_groups, total=total, errors=errors, query=request.query_string, country=params.country, item=params.item, level=params.level, lang=lang[0], translate=translator(lang), gen=gen, opt_date=opt_date, title=title, website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read)


@route('/issues/matrix')
def matrix(db, lang):
    params = Params(default_limit=None)
    errors_groups = query._count(db, params, [
        "markers.item",
        "markers.class",
        "sources.country",
        "items.menu->'en'"]
    )
    analysers = defaultdict(lambda: defaultdict(int))
    analysers_sum = defaultdict(int)
    countries_sum = defaultdict(int)
    total = 0
    for row in errors_groups:
        item, class_, country, menu, count = row
        analyser = '{}/{} {}'.format(item, class_, menu)
        analysers[analyser][country] += count
        analysers_sum[analyser] += count
        countries_sum[country] += count
        total += count

    return template('errors/matrix', total=total, countries_sum=countries_sum, analysers_sum=analysers_sum, analysers=analysers)
