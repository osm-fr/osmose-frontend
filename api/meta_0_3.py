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

from bottle import default_app, route, response, request
from modules import query_meta


app_0_2 = default_app.pop()


def _map_items(categories):
    for categorie in categories:
        categorie['categ'] = categorie['id']
        del categorie['id']
        for item in categorie['items']:
            item['categ'] = item['categorie_id']
            del item['categorie_id']
    return categories


@route('/items')
def items(db, langs):
    return {"categories": _map_items(query_meta._items(db, langs = langs))}


@route('/items/<item:int>/class/<classs:int>')
def items(db, langs, item, classs):
    return {"categories": (query_meta._items(db, item = item, classs = classs, langs = langs))}


@route('/countries')
def items(db):
    return {"countries": query_meta._countries(db)}


@route('/tags')
def items(db):
    return {"tags": query_meta._tags(db)}


default_app.push(app_0_2)
