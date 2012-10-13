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
app.plugins = []

import osmose

application = bottle.default_app()
