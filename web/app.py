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
from bottle import route, view, template, error, redirect, request, hook
from tools import utils, oauth, xmldict
import beaker.middleware
import os
import assets
from modules.osmose_bottle import uuid_filter, ext_filter
from modules import bottle_pgsql
from modules import bottle_cors
from modules import bottle_gettext
from modules import bottle_user


app = bottle.Bottle()
bottle.default_app.push(app)

assets.init_assets()

@hook('before_request')
def setup_request():
    if request:
        request.session = request.environ['beaker.session']

from bottle import SimpleTemplate
SimpleTemplate.defaults["get_url"] = app.get_url

app.install(bottle_pgsql.Plugin(utils.db_string))
# Temporary allow CORS on web
app.install(bottle_cors.Plugin(allow_origin = '*', preflight_methods = ['GET', 'POST', 'PUT', 'DELETE']))
app.install(bottle_gettext.Plugin('osmose-frontend', os.path.join("po", "mo"), utils.allowed_languages))
app.install(bottle_user.Plugin())

app.router.add_filter('uuid', uuid_filter)
app.router.add_filter('ext', ext_filter)


@route('/', name='root')
def index(lang):
    translate = utils.translator(lang)
    return template('index', translate=utils.translator(lang))

@route('/contact')
def contact(lang, name=None):
    translate = utils.translator(lang)
    return template('contact', translate=utils.translator(lang))

@route('/copyright')
def copyright(lang, name=None):
    translate = utils.translator(lang)
    return template('copyright', translate=utils.translator(lang), main_project=utils.main_project, main_website=utils.main_website)

@route('/translation')
def translation(lang, name=None):
    translate = utils.translator(lang)
    return template('translation', translate=utils.translator(lang))

@route('/login')
def login(lang, name=None):
    if request.session.has_key('user'):
        del request.session['user'] # logout
    (url, oauth_tokens) = oauth.fetch_request_token()
    request.session['oauth_tokens'] = oauth_tokens
    request.session.save()
    redirect(url)

@route('/logout')
def login(lang, name=None):
    if request.session.has_key('user'):
        del request.session['user']
        request.session.save()
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
    finally:
        request.session.save()
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
    if 'map/issues/' in request.path:
        return ""
    elif 'images/markers/marker-b-' in request.path:
        redirect('/images/markers/marker-b-0.png')
    elif 'images/markers/marker-l-' in request.path:
        redirect('/images/markers/marker-l-0.png')
    else:
        return {}

import byuser
import issue
import issues
import map
import false_positive
import editor

@route('/<filename:path>', name='static')
def static(filename):
    return bottle.static_file(filename, root='static')


for l in utils.allowed_languages:
    app.mount('/' + l + '/', app)


session_opts = {
    'session.type': 'file',
    'session.data_dir': './session/',
    'session.cookie_expires': False,
}
app_middleware = beaker.middleware.SessionMiddleware(app, session_opts)


if __name__ == '__main__':
    bottle.run(app=app_middleware, host='0.0.0.0', port=20009, reloader=True, debug=True)
else:
    bottle.default_app.pop()
