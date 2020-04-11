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
from modules.osmose_bottle import uuid_filter, ext_filter
from modules import utils
from modules import bottle_pgsql
from modules import bottle_cors
from modules import bottle_langs
from modules import bottle_gettext


class OsmoseAPIBottle(bottle.Bottle):
    def default_error_handler(self, res):
        bottle.response.content_type = 'text/plain'
        return res.body

app_0_3 = OsmoseAPIBottle()
bottle.default_app.push(app_0_3)

app_0_2 = OsmoseAPIBottle()
bottle.default_app.push(app_0_2)


app_0_2.install(bottle_pgsql.Plugin(utils.db_string))
app_0_2.install(bottle_cors.Plugin(allow_origin = '*', preflight_methods = ['GET', 'POST', 'PUT', 'DELETE']))
app_0_2.install(bottle_gettext.Plugin('osmose-frontend', os.path.join("web", "po", "mo"), utils.allowed_languages))

app_0_3.install(bottle_pgsql.Plugin(utils.db_string))
app_0_3.install(bottle_cors.Plugin(allow_origin = '*', preflight_methods = ['GET', 'POST', 'PUT', 'DELETE']))
app_0_3.install(bottle_langs.Plugin())

app_0_2.router.add_filter('ext', ext_filter)
app_0_3.router.add_filter('ext', ext_filter)

app_0_3.router.add_filter('uuid', uuid_filter)

from . import meta_0_2
from . import meta_0_3
from . import user
from . import issue
from . import issues
from . import issues_tiles
from . import false_positive

bottle.default_app.pop()
bottle.default_app.pop()

if __name__ == '__main__':
    bottle.run(app=app_0_3, host='0.0.0.0', port=20009, reloader=True, debug=True)
