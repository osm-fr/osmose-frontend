#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2012 Frederic Rodrigo
#
#

import bottle
from bottle import route, view, template, error, redirect, request, hook
from tools import utils, oauth, xmldict
import beaker.middleware


app = bottle.default_app()

@hook('before_request')
def setup_request():
    request.session = request.environ['beaker.session']

for l in utils.allowed_languages:
    app.mount('/' + l, app)

from bottle import SimpleTemplate
SimpleTemplate.defaults["get_url"] = app.get_url

import bottle_pgsql
app.install(bottle_pgsql.Plugin(utils.db_string))
import bottle_gettext, os
app.install(bottle_gettext.Plugin('osmose-frontend', os.path.join("po", "mo"), utils.allowed_languages))
import bottle_cors
app.install(bottle_cors.Plugin(allow_origin = '*', preflight_methods = ['GET', 'POST', 'PUT', 'DELETE']))

def ext_filter(config):
    regexp = r'html|json|xml|rss|png|svg|pdf|gpx|josm|csv'
    def to_python(match):
        return match if match in ('html', 'json', 'xml', 'rss', 'png', 'svg', 'pdf', 'gpx', 'josm', 'csv') else 'html'
    def to_url(ext):
        return ext
    return regexp, to_python, to_url
app.router.add_filter('ext', ext_filter)

@route('/', name='root')
def index(lang):
    translate = utils.translator(lang)
    return template('index')

@route('/contact')
def contact(lang, name=None):
    translate = utils.translator(lang)
    return template('contact')

@route('/copyright')
def copyright(lang, name=None):
    translate = utils.translator(lang)
    return template('copyright', main_project=utils.main_project, main_website=utils.main_website)

@route('/translation')
def translation(lang, name=None):
    translate = utils.translator(lang)
    return template('translation')

@route('/login')
def login(lang, name=None):
    if request.session.has_key('user'):
        del request.session['user'] # logout
    (url, oauth_tokens) = oauth.fetch_request_token()
    request.session['oauth_tokens'] = oauth_tokens
    redirect(url)

@route('/logout')
def login(lang, name=None):
    if request.session.has_key('user'):
        del request.session['user']
    redirect('map')

@route('/oauth')
def oauth_(lang, name=None):
    try:
        oauth_tokens = request.session['oauth_tokens']
        oauth_tokens = oauth.fetch_access_token(request.session['oauth_tokens'], request)
        request.session['oauth_tokens'] = oauth_tokens
        try:
            user_request = oauth.get(oauth_tokens, utils.remote_url + 'api/0.6/user/details')
            if user_request:
                request.session['user'] = xmldict.xml_to_dict(user_request.encode('utf-8'))
        except Exception as e:
            pass
        if not request.session.has_key('user'):
            request.session['user'] = None
    except:
        pass
    redirect('map')

@route('/josm_proxy')
def josm_proxy():
    query = request.query_string
    r = None
    if query.startswith('errors.josm'):
        r = "http://%s/%s" % (utils.website, query) # Explicit http, not https
    else:
        r = "http://localhost:8111/%s" % query
    return "<img src='%s'/>" % r

@bottle.route('/<:re:.*>', method='OPTIONS')
def enable_cors_generic_route():
    pass

@error(404)
@view('404')
def error404(error):
    if 'images/markers/marker-b-' in request.path:
        redirect('/images/markers/marker-b-0.png')
    if 'images/markers/marker-l-' in request.path:
        redirect('/images/markers/marker-l-0.png')
    else:
        return {}

import api_0_1
import api_0_2_meta
import byuser
import control
import error
import errors
import map
import false_positive
import editor

@route('/<filename:path>', name='static')
def static(filename):
    return bottle.static_file(filename, root='static')


session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.auto': True,
    'session.cookie_expires': False,
}
app = beaker.middleware.SessionMiddleware(app, session_opts)
