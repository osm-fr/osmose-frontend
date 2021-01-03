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

import os
from .tool import tag2link
from modules.query import fixes_default

t2l = tag2link.tag2link(os.path.dirname(os.path.realpath(__file__)) + "/tool/tag2link_sources.xml")


def _get(db, err_id=None, uuid=None):
    columns_marker = [
        "markers.item",
        "markers.source_id", "markers.class",
        "elems", "fixes",
        "lat::float", "lon::float",
        "title", "subtitle", "updates_last.timestamp",
        "detail", "fix", "trap", "example", "source AS source_code", "resource",
    ]

    if err_id:
        sql = "SELECT uuid_to_bigint(markers.uuid) AS id, " + ",".join(columns_marker) + """
        FROM
            markers
            JOIN class ON
                class.item = markers.item AND
                class.class = markers.class
            JOIN updates_last ON
                updates_last.source_id = markers.source_id
        WHERE
            uuid_to_bigint(uuid) = %s
        """
        db.execute(sql, (err_id, ))
    else:
        sql = "SELECT " + ",".join(columns_marker) + """
        FROM
            markers
            JOIN class ON
                class.item = markers.item AND
                class.class = markers.class
            JOIN updates_last ON
                updates_last.source_id = markers.source_id
        WHERE
            uuid = %s
        """
        db.execute(sql, (uuid, ))

    marker = db.fetchone()

    if not marker:
        return None

    marker['fixes'] = fixes_default(marker['fixes'])
    marker['elems'] = list(map(lambda elem: dict(elem,
        type_long={'N':'node', 'W':'way', 'R':'relation'}[elem['type']],
    ), marker['elems'] or []))

    return marker


def _expand_tags(tags, links, short = False):
  t = []
  if short:
    for k in tags:
      t.append({"k": k})
  else:
    for (k, v) in sorted(tags.items()):
      if links and k in links:
        t.append({"k": k, "v": v, "vlink": links[k]})
      else:
        t.append({"k": k, "v": v})
  return t
