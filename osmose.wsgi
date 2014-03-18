#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2012 Frederic Rodrigo
#
#

import os
os.chdir(os.path.dirname(__file__))

import sys
sys.path.append(os.path.dirname(__file__))

# Need for reset plugin in wsgi
import bottle
app = bottle.default_app()
app.plugins = filter(lambda x: isinstance(x,bottle.JSONPlugin) or isinstance(x,bottle.HooksPlugin) or isinstance(x,bottle.TemplatePlugin), app.plugins)

import osmose

application = osmose.app
