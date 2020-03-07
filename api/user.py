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
from tools.OrderedDict import OrderedDict
from user_utils import _user, _user_count


app_0_2 = default_app.pop()


@app_0_2.route('/user/<username>')
@route('/user/<username>')
def user(db, lang, username):
    params, username, errors = _user(db, lang, username)

    out = OrderedDict()
    for res in errors:
        res["timestamp"] = str(res["timestamp"])
        res["lat"] = float(res["lat"])
        res["lon"] = float(res["lon"])
    out["issues"] = map(dict, errors)
    return out


@app_0_2.route('/user_count/<username>')
@route('/user_count/<username>')
def user_count(db, lang, username=None, format=None):
    count = _user_count(db, username)
    return count


default_app.push(app_0_2)
