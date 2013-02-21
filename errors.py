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
import StringIO, re

import errors_graph


def _errors(db, lang, params):
    results = query._gets(db, params)
    out = OrderedDict()

    if not params.full:
        out["description"] = ["lat", "lon", "error_id", "item"]
    else:
        out["description"] = ["lat", "lon", "error_id", "item", "source", "classs", "elems", "subclass", "subtitle", "title", "level", "update", "username"]
    out["errors"] = []

    translate = utils.translator(lang)

    for res in results:
        lat       = str(float(res["lat"])/1000000)
        lon       = str(float(res["lon"])/1000000)
        error_id  = res["id"]
        item      = res["item"] or 0

        if not params.full:
            out["errors"].append([lat, lon, str(error_id), str(item)])
        else:
            source    = res["source"]
            classs    = res["class"]
            elems     = res["elems"]
            subclass  = res["subclass"]
            subtitle  = translate.select(res["subtitle"])
            title     = translate.select(res["title"])
            level     = res["level"]
            update    = res["timestamp"]
            username  = (res["username"] or "").decode('utf-8')
            out["errors"].append([lat, lon, str(error_id), str(item), str(source), str(classs), str(elems), str(subclass), subtitle, title, str(level), str(update), username])

    return out


@route('/api/0.2/errors')
def errors(db, lang):
    params = query._params()
    return _errors(db, lang, params)


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
def index_redirect():
    redirect("errors/")


@route('/errors/')
@route('/errors/done')
@route('/errors/false-positive')
def index(db, lang):
    if request.path.endswith("false-positive"):
        title = _("False positives")
        gen = "false-positive"
    elif request.path.endswith("done"):
        title = _("Fixed errors")
        gen = "done"
    else:
        title = _("Informations")
        gen = "info"

    countries = query_meta._countries(db, lang)
    items = query_meta._items(db, lang)

    params = query._params()
    limit = request.params.get('limit', type=int)
    if limit >= 0 and params.limit <= 10000:
        params.limit = limit
    params.status = {"info":"open", "false-positive": "false", "done":"done"}[gen]

    errors_groups = query._count(db, params, [
        "dynpoi_class.item",
        "dynpoi_class.source",
        "dynpoi_class.class",
        "dynpoi_source.comment"],
        ["dynpoi_item"], [
        "first(dynpoi_item.menu) AS menu",
        "first(dynpoi_class.title) AS title"],
        orderBy = True)

    total = 0
    for res in errors_groups:
        if res["count"] != -1:
            total += res["count"]

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

    return template('errors/index', countries=countries, items=items, errors_groups=errors_groups, total=total, errors=errors, query=request.query_string, country=params.country, item=params.item, translate=utils.translator(lang), gen=gen, opt_date=opt_date, title=title)
