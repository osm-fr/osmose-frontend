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

from bottle import route, template, redirect, response, html_escape
from modules import utils
from modules.utils import i10n_select_auto
from modules import query

from api.user_utils import _user, _user_count


@route('/byuser')
def byUser():
    redirect("byuser/")


@route('/byuser/<username>.<format:ext>')
def user(db, lang, username=None, format=None):
    params, username, errors = _user(db, lang, username)

    for error in errors:
        error["subtitle"] = i10n_select_auto(error["subtitle"], lang)
        error["title"] = i10n_select_auto(error["title"], lang)
        error["menu"] = i10n_select_auto(error["menu"], lang)
        error['timestamp'] = str(error['timestamp'])

    count = len(errors)

    if format == 'rss':
        response.content_type = "application/rss+xml"
        return template('byuser/byuser.rss', username=username, users=params.users, count=count, errors=errors, website=utils.website + '/' + lang[0])
    else:
        return dict(username=username, users=params.users, count=count, errors=list(map(dict, errors)), website=utils.website + '/' + lang[0], main_website=utils.main_website, remote_url_read=utils.remote_url_read)


@route('/byuser_count/<username>')
@route('/byuser_count/<username>.<format:ext>')
def user_count(db, lang, username=None, format=None):
    count = _user_count(db, username)

    if format == 'rss':
        response.content_type = "application/rss+xml"
        return template('byuser/byuser_count.rss', username=username, count=count, website=utils.website)
    else:
        return count
