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

from bottle import route, request, response, redirect
from modules_legacy import utils
from modules_legacy.utils import i10n_select_auto
from modules_legacy.params import Params
from modules_legacy import query
from modules_legacy import query_meta
from collections import defaultdict
import io, re

from . import errors_graph


@route('/issues/graph.<format:ext>')
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


@route('/issues/open.<format:ext>')
@route('/issues/done.<format:ext>')
@route('/issues/false-positive.<format:ext>')
def index(db, lang, format):
    if "false-positive" in request.path:
        gen = "false-positive"
    elif "done" in request.path:
        gen = "done"
    else:
        gen = "issue"

    params = Params()
    params.status = {"issue":"open", "false-positive": "false", "done":"done"}[gen]
    params.fixable = None

    items = query_meta._items_menu(db, lang)
    for res in items:
        if params.item == str(res["item"]):
            title += ' - ' + res['menu']['auto']

    params.limit = request.params.get('limit', type=int, default=100)
    if params.limit > 10000:
        params.limit = 10000

    params.full = True
    errors = query._gets(db, params)
    for error in errors:
        error["subtitle"] = i10n_select_auto(error["subtitle"], lang)
        error["title"] = i10n_select_auto(error["title"], lang)
        error["menu"] = i10n_select_auto(error["menu"], lang)

    countries = query_meta._countries(db)
    items = list(map(dict, items))

    if params.item:
        params.limit = None
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
            res["title"] = i10n_select_auto(res["title"], lang)
            res["menu"] = i10n_select_auto(res["menu"], lang)
            if res["count"] != -1:
                total += res["count"]
    else:
        errors_groups = []
        total = 0

    if gen in ("false-positive", "done"):
        opt_date = "date"
    else:
        opt_date = None

    errors_groups = list(map(dict, errors_groups))
    for res in errors_groups:
        res['timestamp'] = str(res['timestamp'])
    errors = list(map(dict, errors))
    for res in errors:
        res['timestamp'] = str(res['timestamp'])
        if 'date' in res:
            res['date'] = str(res['date'])
    return dict(countries=countries, items=items, errors_groups=errors_groups, total=total, errors=errors, gen=gen, opt_date=opt_date, website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read)


@route('/issues/matrix.json')
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

    return dict(total=total, countries_sum=countries_sum, analysers_sum=analysers_sum, analysers=analysers)
