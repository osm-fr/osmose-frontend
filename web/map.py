#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
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

from bottle import route, request, template, redirect
from modules.params import Params
from modules import utils, query, query_meta
from .tool.translation import translator
from api.user_utils import _user_count
from collections import defaultdict


@route('/map')
def index_redirect():
    new_url = "map/"
    if request.query_string:
        new_url += "#" + request.query_string
    redirect(new_url)

@route('/map/')
def index(db, user, lang):
    if request.query_string:
        redirect("./#" + request.query_string)

    tags = query_meta._tags(db)

    categories = query_meta._items(db, langs = lang)

    item_tags = defaultdict(set)
    item_levels = {'1': set(), '2': set(), '3': set()}
    for categ in categories:
        for item in categ['items']:
            for level in item['levels']:
                item_levels[str(level['level'])].add(item['item'])
            if item['tags']:
                for tag in item['tags']:
                    item_tags[tag].add(item['item'])

    item_levels['1,2'] = item_levels['1'] | item_levels['2']
    item_levels['1,2,3'] = item_levels['1,2'] | item_levels['3']

    urls = []
    # TRANSLATORS: link to help in appropriate language
    if user:
        urls.append(("byuser", _("Issues by user"), "../byuser/"))
    # TRANSLATORS: link to source code
    urls.append(("statistics", _("Statistics"), "../control/update_matrix"))

    helps = []
    helps.append((_("Contact"), "../contact"))
    helps.append((_("Help on wiki"), _("http://wiki.openstreetmap.org/wiki/Osmose")))
    helps.append((_("Copyright"), "../copyright"))
    helps.append((_("Sources"), "https://github.com/osm-fr?q=osmose"))
    helps.append((_("Translation"), "../translation"))

    sql = """
SELECT
    EXTRACT(EPOCH FROM ((now())-timestamp)) AS age
FROM
    updates_last
ORDER BY
    timestamp
LIMIT
    1
OFFSET
    (SELECT COUNT(*)/2 FROM updates_last)
;
"""
    db.execute(sql)
    delay = db.fetchone()
    if delay and delay[0]:
        delay = delay[0]/60/60/24
    else:
        delay = 0

    if user != None:
        if user:
            user_error_count = _user_count(db, user)
        else: # user == False
            user = '[user name]'
            user_error_count = {1: 0, 2: 0, 3: 0}
    else:
        user_error_count = None

    return template('map/index', categories=categories, item_tags=item_tags, tags=tags, item_levels=item_levels,
        main_project=utils.main_project, urls=urls, helps=helps, delay=delay, languages_name=utils.languages_name, translate=translator(lang),
        website=utils.website, remote_url_read=utils.remote_url_read, request=request,
        user=user, user_error_count=user_error_count)


def _errors_geo(db, params):
    results = query._gets(db, params)

    features = []

    for res in results:
        properties = {"error_id": res["uuid"], "item": res["item"] or 0}
        features.append({"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(res["lon"]), float(res["lat"])]}, "properties": properties})

    return {"type": "FeatureCollection", "features": features}


@route('/map/markers')
def markers(db):
    params = Params()

    if (not params.users) and (not params.source) and (params.zoom < 7):
        return

    params.limit = 200
    params.full = False

    return _errors_geo(db, params)


@route('/tpl/popup.tpl')
def popup_template(lang):
    return template('map/popup', mustache_delimiter="{{={% %}=}}", website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read)

@route('/tpl/doc.tpl')
def doc_template(lang):
    return template('map/doc', mustache_delimiter="{{={% %}=}}", website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read)

@route('/tpl/editor.tpl')
def editor_template(lang):
    return template('map/editor', mustache_delimiter="{{={% %}=}}", main_website=utils.main_website)
