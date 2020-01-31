#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rorigo 2018                                       ##
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

from bottle import route, response, request
from tools import query_meta


@route('/api/0.3beta/items')
def items(db):
    langs = request.params.get('langs')
    return {"categories": query_meta._items_3(db, langs = langs)}


# langs = Accept-Language compatible string
@route('/api/0.3beta/items/<item:int>/class/<classs:int>')
def items(db, item, classs):
    langs = request.params.get('langs')
    return {"categories": query_meta._items_3(db, item = item, classs = classs, langs = langs)}


@route('/api/0.3beta/countries')
def items(db):
    return {"countries": query_meta._countries_3(db)}


@route('/api/0.3beta/tags')
def items(db):
    return {"tags": query_meta._tags(db)}
