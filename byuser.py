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
from tools import query
from tools.OrderedDict import OrderedDict


@route('/byuser')
def byUser():
    redirect("byuser/")


@route('/byuser/')
@route('/byuser/<username>')
@route('/byuser/<username>.<format:ext>')
@route('/api/0.2/user/<username>')
def user(db, lang, username=None, format=None):
    params = query._params()
    if username:
        params.username = username.decode("utf-8")
    params.limit = 500
    params.full = True

    if not params.username:
        return template('byuser/index')

    results = query._gets(db, params)
    count = len(results)
    if request.path.startswith("/api") or format == "json":
        out = OrderedDict()
        out["description"] = ["id", "item", "lat", "lon", "source", "class", "elems", "subclass", "subtitle", "comment", "title", "level", "timestamp", "menu", "username", "date"]
        for res in results:
            res["timestamp"] = str(res["timestamp"])
            res["date"] = str(res["date"])
        out["byusers"] = results
        return out

    elif format == 'rss':
        response.content_type = "application/rss+xml"
        return template('byuser/byuser.rss', username=params.username, count=count, results=results, translate=utils.translator(lang))

    else:
        return template('byuser/byuser', username=params.username, count=count, results=results, translate=utils.translator(lang))


def _users(db):
    params = query._params()
    return query._count(db, params, ["marker_elem.username"])


@route('/byuser-stats')
def byuser_stats(db):
    return template('byuser/byuser-stats', results=_users(db))


@route('/api/0.2/users')
def users(db):
    out = OrderedDict()
    out["description"] = ["username", "count"]
    out["users"] = _users(db)
    return out
