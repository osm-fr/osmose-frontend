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

from bottle import route, response
from .tools import query_meta


@route('/meta/class')
def items(db, lang):
    return {"class": query_meta._class(db, lang)}


@route('/meta/items')
def items(db, lang):
    return {"items": query_meta._items(db, lang)}


@route('/meta/countries')
def items(db, lang):
    return {"countries": map(lambda x: x[0], query_meta._countries(db, lang))}


@route('/meta/categories')
def items(db, lang):
    return {"categories": query_meta._categories(db, lang)}


@route('/meta/tags')
def items(db, lang):
    return {"tags": query_meta._tags(db)}
