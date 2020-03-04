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

from tools import tag2link
from tools.query import fixes_default

t2l = tag2link.tag2link("tools/tag2link_sources.xml")


def _get(db, err_id=None, uuid=None):
    columns_marker = ["marker.item", "marker.source", "marker.class", "marker.elems", "marker.fixes",
        "marker.lat", "marker.lon",
        "class.title", "marker.subtitle", "dynpoi_class.timestamp",
        "class.detail", "class.fix", "class.trap", "class.example", "class.source AS source_code", "class.resource",
        ]

    if err_id:
        sql = "SELECT uuid_to_bigint(marker.uuid) AS id, " + ",".join(columns_marker) + """
        FROM
            marker
            JOIN dynpoi_class ON
                marker.source = dynpoi_class.source AND
                marker.class = dynpoi_class.class
            JOIN class ON
                marker.item = class.item AND
                marker.class = class.class
        WHERE
            uuid_to_bigint(marker.uuid) = %s
        """
        db.execute(sql, (err_id, ))
    else:
        sql = "SELECT " + ",".join(columns_marker) + """
        FROM
            marker
            JOIN dynpoi_class ON
                marker.source = dynpoi_class.source AND
                marker.class = dynpoi_class.class
            JOIN class ON
                marker.item = class.item AND
                marker.class = class.class
        WHERE
            marker.uuid = %s
        """
        db.execute(sql, (uuid, ))

    marker = db.fetchone()

    if not marker:
        return None

    marker['fixes'] = fixes_default(marker['fixes'])
    marker['elems'] = map(lambda elem: dict(elem,
        type_long={'N':'node', 'W':'way', 'R':'relation'}[elem['type']],
    ), marker['elems'] or [])

    return marker


def _expand_tags(tags, links, short = False):
  t = []
  if short:
    for k in tags:
      t.append({"k": k})
  else:
    for (k, v) in sorted(tags.items()):
      if links and links.has_key(k):
        t.append({"k": k, "v": v, "vlink": links[k]})
      else:
        t.append({"k": k, "v": v})
  return t
