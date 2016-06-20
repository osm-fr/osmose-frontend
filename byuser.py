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

from bottle import route, request, template, redirect, response, html_escape
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
        params.users = utils.pg_escape(username.decode("utf-8")).split(",")
    params.limit = 500
    params.full = True
    username = ",".join(params.users)

    if not params.users:
        return template('byuser/index')

    errors = query._gets(db, params)
    count = len(errors)
    if request.path.startswith("/api") or format == "json":
        out = OrderedDict()
        out["description"] = ["id", "item", "lat", "lon", "source", "class", "elems", "subclass", "subtitle", "comment", "title", "level", "timestamp", "menu", "username", "date"]
        for res in errors:
            res["timestamp"] = str(res["timestamp"])
            res["date"] = str(res["date"])
        out["byusers"] = errors
        return out

    elif format == 'rss':
        response.content_type = "application/rss+xml"
        return template('byuser/byuser.rss', username=username, users=params.users, count=count, errors=errors, translate=utils.translator(lang), website=utils.website)

    else:
        return template('byuser/byuser', username=username, users=params.users, count=count, errors=errors, translate=utils.translator(lang), website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read, html_escape=html_escape)


def _user_count(db, username=None):
    params = query._params()
    if username:
        params.users = utils.pg_escape(username.decode("utf-8")).split(",")

    if not params.users:
        return

    res = query._count(db, params, ['dynpoi_class.level'], ['dynpoi_class.level'])
    ret = {1:0, 2:0, 3:0}
    for (l, c) in res:
        ret[l] = c

    return ret


@route('/byuser_count/<username>')
@route('/byuser_count/<username>.<format:ext>')
@route('/api/0.2/user_count/<username>')
def user_count(db, lang, username=None, format=None):
    count = _user_count(db, username)
    if request.path.startswith("/api") or format == "json":
        return count

    elif format == 'rss':
        response.content_type = "application/rss+xml"
        return template('byuser/byuser_count.rss', username=username, count=count, translate=utils.translator(lang), website=utils.website)

    else:
        return count


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
