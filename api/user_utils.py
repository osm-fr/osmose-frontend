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

from modules.params import Params
from tools import query


def _user(db, lang, username):
    params = Params()
    if username:
        params.users = username.split(",")
    params.limit = 500
    params.full = True
    username = ",".join(params.users)

    errors = query._gets(db, params)
    return [params, username, errors]


def _user_count(db, username=None):
    params = Params()
    if username:
        params.users = username.split(",")

    if not params.users:
        return

    res = query._count(db, params, ['class.level'], ['class.level'])
    ret = {1:0, 2:0, 3:0}
    for (l, c) in res:
        ret[l] = c

    return ret
