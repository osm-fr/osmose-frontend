#! /usr/bin/env python
#-*- coding: utf-8 -*-
###########################################################################
##                                                                       ##
## Copyrights Jocelyn Jaubert 2013                                       ##
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

from bottle import route, template, abort
from .tool.translation import translator

from api.false_positive_utils import _get


@route('/false-positive/<uuid:uuid>.json')
def fp_(db, lang, uuid):
    marker, columns = _get(db, 'false', uuid=uuid)
    if not marker:
        abort(410, "Id is not present in database.")

    marker = dict(marker)
    marker['timestamp'] = str(marker['timestamp'])
    return dict(
        uuid=uuid,
        marker=marker,
    )
