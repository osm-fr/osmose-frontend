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

from bottle import route
from tools import utils
from tools import query
from tools.OrderedDict import OrderedDict


def _user(db, lang, username):
    params = query._params()
    if username:
        params.users = utils.pg_escape(username.decode("utf-8")).split(",")
    params.limit = 500
    params.full = True
    username = ",".join(params.users)

    errors = query._gets(db, params)
    return [params, username, errors]

@route('/api/0.2/user/<username>')
@route('/api/0.3beta/user/<username>')
def user(db, lang, username):
    params, username, errors = _user(db, lang, username)

    out = OrderedDict()
    for res in errors:
        res["timestamp"] = str(res["timestamp"])
        res["lat"] = float(res["lat"])
        res["lon"] = float(res["lon"])
    out["issues"] = map(dict, errors)
    return out


def _user_count(db, username=None):
    params = query._params()
    if username:
        params.users = utils.pg_escape(username.decode("utf-8")).split(",")

    if not params.users:
        return

    res = query._count(db, params, ['class.level'], ['class.level'])
    ret = {1:0, 2:0, 3:0}
    for (l, c) in res:
        ret[l] = c

    return ret


@route('/api/0.2/user_count/<username>')
@route('/api/0.3beta/user_count/<username>')
def user_count(db, lang, username=None, format=None):
    count = _user_count(db, username)
    return count
