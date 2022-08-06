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

import asyncio
from bottle import route, redirect, response, html_escape, request
from modules.dependencies.database import get_dbconn
from modules.dependencies.commons_params import params as async_params
from modules_legacy import utils
from modules_legacy.utils import i10n_select_auto
from modules_legacy import query
from lxml import etree
from lxml.builder import E, ElementMaker

from api.user_utils import _user, _user_count


@route('/byuser')
def byUser():
    redirect("byuser/")


@route('/byuser/<username>.<format:ext>')
def user(db, lang, username=None, format=None):
    if format == 'rss' or format == 'gpx' or format == 'kml':
        response.status = 301
        response.set_header('Location', f"https://{utils.website}/api/0.3/issues.{format}?{request.query_string}&username={username}")
        return

    async def t(username):
        return await _user(await async_params(), await get_dbconn(), username)
    params, username, errors = asyncio.run(t(username))

    for error in errors:
        error["subtitle"] = i10n_select_auto(error["subtitle"], lang)
        error["title"] = i10n_select_auto(error["title"], lang)
        error["menu"] = i10n_select_auto(error["menu"], lang)

    count = len(errors)
    for error in errors:
        error['timestamp'] = str(error['timestamp'])
        error['uuid'] = str(error['uuid'])
    return dict(username=username, users=params.users, count=count, errors=list(map(dict, errors)), website=utils.website + '/' + lang[0], main_website=utils.main_website, remote_url_read=utils.remote_url_read)


@route('/byuser_count/<username>.rss')
def user_count(db, lang, username=None):
    async def t(username):
        return await _user_count(await async_params(), await get_dbconn(), username)
    count = asyncio.run(t(username))
    response.content_type = "application/rss+xml"
    xml = E.rss(
        E.channel(
            E.title('Osmose - ' + username),
            E.description(_("Statistics for user {0}").format(username)),
            E.link('http://{}/byuser/{}'.format(utils.website, username)),
            E.item(
                E.title(_("Number of level {level} issues: {count}").format(level=1, count=count[1]))
            ),
            E.item(
                E.title(_("Number of level {level} issues: {count}").format(level=2, count=count[2]))
            ),
            E.item(
                E.title(_("Number of level {level} issues: {count}").format(level=3, count=count[3]))
            ),
        ),
        version = '2.0',
    )
    return etree.tostring(xml, pretty_print=True)


@route('/byuser_count/<username>')
def user_count(db, lang, username=None):
    async def t(username):
        return await _user_count(await async_params(), await get_dbconn(), username)
    return asyncio.run(t(username))
