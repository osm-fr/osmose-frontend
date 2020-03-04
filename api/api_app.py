#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frederic Rodrigo 2020                                      ##
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

import bottle
from modules.osmose_bottle import uuid_filter, ext_filter
from tools import utils
from modules import bottle_pgsql
from modules import bottle_cors
from modules import bottle_langs


class OsmoseAPIBottle(bottle.Bottle):
    def default_error_handler(self, res):
        bottle.response.content_type = 'text/plain'
        return res.body

app = OsmoseAPIBottle()
bottle.default_app.push(app)

app.install(bottle_pgsql.Plugin(utils.db_string))
app.install(bottle_cors.Plugin(allow_origin = '*', preflight_methods = ['GET', 'POST', 'PUT', 'DELETE']))
app.install(bottle_langs.Plugin(utils.allowed_languages))

app.router.add_filter('uuid', uuid_filter)
app.router.add_filter('ext', ext_filter)

import api_0_2_meta
import api_0_3_meta
import api_user
import api_issue
import api_issues
import api_issues_tiles
import api_false_positive


if __name__ == '__main__':
    bottle.run(app=app, host='0.0.0.0', port=20009, reloader=True, debug=True)
