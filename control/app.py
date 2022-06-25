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
import os
from modules_legacy import utils
from modules_legacy import bottle_pgsql


class OsmoseControlBottle(bottle.Bottle):
    def default_error_handler(self, res):
        bottle.response.content_type = 'text/plain'
        return res.body

app = OsmoseControlBottle()
bottle.default_app.push(app)

app.install(bottle_pgsql.Plugin(utils.db_string))

from . import control

bottle.default_app.pop()

if __name__ == '__main__':
    bottle.run(app=app, host='0.0.0.0', port=20009, reloader=True, debug=True)
