#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2012 Frederic Rodrigo
#
#

import bottle
from bottle import route, view, template, error

from tools import utils

app = bottle.default_app()

from bottle import SimpleTemplate
SimpleTemplate.defaults["get_url"] = app.get_url

import bottle_pgsql_pool
app.install(bottle_pgsql_pool.Plugin("host='localhost' dbname='%s' user='%s' password='%s'" % (utils.pg_base, utils.pg_user, utils.pg_pass), dictrows=False))
import bottle_gettext, os
app.install(bottle_gettext.Plugin('osmose-frontend', os.path.join("po", "mo"), utils.allowed_languages))

def ext_filter(config):
    regexp = r'html|json|xml'
    def to_python(match):
        return match if match in ('html', 'json', 'xml') else 'html'
    def to_url(ext):
        return ext
    return regexp, to_python, to_url
app.router.add_filter('ext', ext_filter)

@route('/', name='root')
@view('index')
def index():
    return {}

@route('/copyright')
@view('copyright')
def copyright(name=None):
    return {}

@error(404)
@view('404')
def error404(error):
    return {}

import api_0_1
import byuser
import control
import error
import errors
import map

@route('/<filename:path>', name='static')
def static(filename):
    return bottle.static_file(filename, root='static')
