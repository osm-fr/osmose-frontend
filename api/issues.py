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

from bottle import default_app, route
from .tools import utils
from .tools import query
from collections import OrderedDict


app_0_2 = default_app.pop()


@app_0_2.route('/errors')
def errors(db, lang):
    params = query._params()
    results = query._gets(db, params)
    out = OrderedDict()

    if not params.full:
        out["description"] = ["lat", "lon", "error_id", "item"]
    else:
        out["description"] = ["lat", "lon", "error_id", "item", "source", "class", "elems", "subclass", "subtitle", "title", "level", "update", "username"]
    out["errors"] = []

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

            subtitle  = utils.i10n_select(res['subtitle'], lang)
            subtitle  = subtitle and subtitle['auto'] or ''

            title     = utils.i10n_select(res['title'], lang)
            title     = title and title['auto'] or ''

            level     = res["level"]
            update    = res["timestamp"]
            username  = ','.join(map(lambda elem: "username" in elem and elem["username"] or "", res['elems'] or []))
            out["errors"].append([str(lat), str(lon), str(error_id), str(item), str(source), str(classs), str(elems), str(subclass), subtitle, title, str(level), str(update), username])

    return out


@route('/issues')
def errors(db, langs):
    params = query._params(max_limit=10000)
    results = query._gets(db, params)

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
                'class': res["class"],
                'subtitle': utils.i10n_select(res["subtitle"], langs),
                'title': utils.i10n_select(res["title"], langs),
                'level': res["level"],
                'update': str(res["timestamp"]),
                'usernames': map(lambda elem: "username" in elem and elem["username"] or "", res['elems'] or []),
            })
        out.append(i)

    return {'issues': out}


default_app.push(app_0_2)
