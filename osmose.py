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
from modules import utils

bottle.TEMPLATE_PATH.insert(0, './web/views/')


app = bottle.default_app()

####### Monkey patch bootle 0.12 - To be removed on 0.13
# https://github.com/bottlepy/bottle/issues/602#issuecomment-591434275
import functools
def pathinfo_adjust_wrapper(func):
    # A wrapper for _handle() method
    @functools.wraps(func)
    def _(environ):
        environ["PATH_INFO"] = environ["PATH_INFO"].encode("utf8").decode("latin1")
        return func(environ)
    return _
app._handle = pathinfo_adjust_wrapper(app._handle)
#######

from modules import bottle_gettext
import os
app.install(bottle_gettext.Plugin('osmose-frontend', os.path.join("web", "po", "mo"), utils.allowed_languages))

from web import app as web_app
for l in utils.allowed_languages:
  app.mount('/' + l, web_app.app)

@app.route('/')
@app.route('/map')
@app.route('/map/')
def index(lang):
    # Route to force a redirect, for missing langue in URL
    pass

from control import app as control_app
app.mount('/control/', control_app.app)

from api import app as api_app
web_app.app.mount('api/0.2/', api_app.app_0_2)
app.mount('/api/0.3beta/', api_app.app_0_3)

app_middleware = web_app.app_middleware

import modules.osmose_bottle
