#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2020                                      ##
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

from bottle import request
from tools import utils
import re


class Params:
    def __init__(self, max_limit = 500):
        self.bbox       = request.query.getunicode('bbox', default=None)
        self.item       = request.query.getunicode('item')
        self.source     = request.query.getunicode('source', default='')
        self.classs     = request.query.getunicode('class', default='')
        self.users      = request.query.getunicode('username', default='')
        self.level      = request.query.getunicode('level', default='1,2,3')
        self.full       = request.query.getunicode('full', default=False)
        self.zoom       = request.query.get('zoom', type=int, default=10)
        self.limit      = request.query.get('limit', type=int, default=100)
        self.country    = request.query.getunicode('country', default=None)
        self.useDevItem = request.query.getunicode('useDevItem', default=False)
        self.status     = request.query.getunicode('status', default="open")
        self.start_date = request.query.getunicode('start_date', default=None)
        self.end_date   = request.query.getunicode('end_date', default=None)
        self.tags       = request.query.getunicode('tags', default=None)
        self.fixable    = request.query.getunicode('fixable', default=None)
        self.osm_type   = request.query.getunicode('osm_type', default=None)
        self.osm_id     = request.query.get('osm_id', type=int, default=None)
        self.tilex      = request.query.getunicode('tilex', default=None)
        self.tiley      = request.query.getunicode('tiley', default=None)

        if self.level:
            self.level = self.level.split(",")
            try:
                self.level = ",".join([str(int(x)) for x in self.level if x])
            except:
                self.level = "1,2,3"
        if self.bbox:
            try:
                self.bbox = list(map(lambda x: float(x), self.bbox.split(',')))
            except:
                self.bbox = None
        if self.users:
            self.users = self.users.split(",")
        if self.limit > max_limit:
            self.limit = max_limit
        if self.country and not re.match(r"^([a-z_]+)(\*|)$", self.country):
            self.country = ''
        if self.useDevItem == "true":
            self.useDevItem = True
        elif self.useDevItem == "all":
            pass
        else:
            self.useDevItem = False
        if self.start_date:
            self.start_date = utils.str_to_datetime(self.start_date)
        if self.end_date:
            self.end_date = utils.str_to_datetime(self.end_date)
        if self.tags:
            self.tags = self.tags.split(",")

        if self.osm_type and self.osm_type not in ['node', 'way', 'relation']:
            self.osm_type = None
        if self.osm_id and not self.osm_type:
            self.osm_id = None
