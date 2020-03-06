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

from bottle import route, request, template, response, abort
import StringIO, os, tempfile, copy

from tools import osmose_common
from tools import utils
from tools import tag2link
from tools import OsmSax
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
        abort(410, "Id is not present in database.")

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


@route('/error/<uuid:uuid>')
def display(db, lang, user, uuid):
    marker = _get(db, uuid=uuid)

    data_type = { "N": "node", "W": "way", "R": "relation", "I": "infos"}

    for e in marker['elems'] or []:
        e['tags'] = _expand_tags(e.get('tags', {}), t2l.checkTags(e.get('tags', {})))

    for fix_group in marker['fixes'] or []:
      for f in fix_group:
        f['create'] = _expand_tags(f['create'], t2l.checkTags(f['create']))
        f['modify'] = _expand_tags(f['modify'], t2l.checkTags(f['modify']))
        f['delete'] = _expand_tags(f['delete'], {}, True)

    return template('error/index', translate=utils.translator(lang), uuid=uuid,
        marker=marker,
        user=user,
        main_website=utils.main_website, data_type=data_type)


@route('/api/0.3beta/issue/<uuid:uuid>/fresh_elems')
@route('/api/0.3beta/issue/<uuid:uuid>/fresh_elems/<fix_num:int>')
def fresh_elems_uuid(db, lang, uuid, fix_num=None):
    data_type = { "N": "node", "W": "way", "R": "relation", "I": "infos"}

    marker = _get(db, uuid=uuid)

    def expand_tags(tags):
      t = []
      for (k, v) in tags.items():
        t.append({"k": k, "v": v})
      return t

    elems = {}
    for elem in marker['elems']:
      if elem['type']:
        fresh_elem = utils.fetch_osm_elem(data_type[elem['type']], elem['id'])

        if fresh_elem and len(fresh_elem) > 0:
            tmp_elem = {data_type[elem['type']]: True,
                    "type": data_type[elem['type']],
                    "id": elem["id"],
                    "version": fresh_elem["version"],
                    "tags": fresh_elem[u'tag'],
                   }
            elems[data_type[elem['type']] + str(elem['id'])] = tmp_elem

    ret = {
        "uuid": uuid,
        "elems": elems.values(),
    }

    if fix_num != None:
      ret["fix"] = {}
      for res in marker['fixes'][fix_num]:
        tid = data_type[res['type']] + str(res['id'])
        if elems.has_key(tid):
            fix_elem_tags = copy.copy(elems[tid]["tags"])
            for k in res['delete']:
                if fix_elem_tags.has_key(k):
                    del fix_elem_tags[k]
            for (k, v) in res['create'].items():
                fix_elem_tags[k] = v
            for (k, v) in res['modify'].items():
                fix_elem_tags[k] = v

            ret["fix"][tid] = fix_elem_tags

    for elem in ret['elems']:
        elem["tags"] = expand_tags(elem["tags"])

    return ret


@route('/api/0.2/error/<err_id:int>')
def error_err_id(db, lang, err_id):
    return _error(2, db, lang, None, _get(db, err_id=err_id))

@route('/api/0.3beta/issue/<uuid:uuid>')
def error_uuid(db, lang, uuid):
    return _error(3, db, lang, uuid, _get(db, uuid=uuid))

def _error(version, db, lang, uuid, marker):
    data_type = { "N": "node", "W": "way", "R": "relation", "I": "infos"}

    # TRANSLATORS: link to tooltip help
    url_help = _("http://wiki.openstreetmap.org/wiki/Osmose/errors")

    translate = utils.translator(lang)

    lat       = str(marker["lat"])
    lon       = str(marker["lon"])
    title     = translate.select(marker["title"])
    subtitle  = translate.select(marker["subtitle"])
    b_date    = marker["timestamp"] or ""
    item      = marker["item"] or 0
    classs    = marker["class"] or 0

    elems = []
    for elem in marker['elems'] or []:
      if elem['type']:
        tags = elem.get("tags", {})
        tmp_elem = {data_type[elem['type']]: True,
                    "type": data_type[elem['type']],
                    "id": elem["id"],
                    "tags": _expand_tags(tags, t2l.checkTags(tags)),
                    "fixes": [],
                   }
        for fix_index, fix_group in enumerate(marker['fixes'] or []):
          for fix in fix_group:
            if (fix['type'] and
                fix['type'] == elem['type'] and
                fix['id'] == elem["id"]):
              tmp_elem["fixes"].append({"num": fix_index,
                                      "add": _expand_tags(fix['create'], t2l.checkTags(fix['create'])),
                                      "mod": _expand_tags(fix['modify'], t2l.checkTags(fix['modify'])),
                                      "del": _expand_tags(fix['delete'], {}, True),
                                     })
        elems.append(tmp_elem)

    new_elems = []
    for fix_index, fix_group in enumerate(marker['fixes'] or []):
      for fix in fix_group:
        if fix['type']:
            found = False
            for e in elems:
                if (e["type"] == data_type[fix['type']] and
                    e["id"] == fix['id']):

                    found = True
                    break
            if not found:
                new_elems.append({"num": fix_index,
                                  "add": _expand_tags(fix['create'], t2l.checkTags(fix['create'])),
                                  "mod": _expand_tags(fix['modify'], t2l.checkTags(fix['modify'])),
                                  "del": _expand_tags(fix['delete'], {}, True),
                                 })

    if version == 2:
        return {
            "lat":lat, "lon":lon,
            "minlat": float(lat) - 0.002, "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002, "maxlon": float(lon) + 0.002,
            "error_id":marker['id'],
            "title":title, "subtitle":subtitle,
            "b_date":b_date.strftime("%Y-%m-%d"),
            "item":item,
            "class":classs,
            "elems":elems, "new_elems":new_elems,
            "elems_id":','.join(map(lambda elem: elem['type_long'] + str(elem['id']), marker["elems"])),
            "url_help":url_help
        }
    else:
        return {
            "lat":lat, "lon":lon,
            "minlat": float(lat) - 0.002, "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002, "maxlon": float(lon) + 0.002,
            "uuid":uuid,
            "title":title, "subtitle":subtitle,
            "b_date":b_date.strftime("%Y-%m-%d"),
            "item":item,
            "class":classs,
            "elems":elems, "new_elems":new_elems,
            "url_help":url_help
        }


@route('/api/0.2/error/<err_id:int>/<status:re:(done|false)>')
def status_err_id(err_id, status):
    if osmose_common.remove_bug_err_id(err_id, status) == 0:
        return
    else:
        abort(410, "FAIL")

@route('/api/0.3beta/issue/<uuid:uuid>/<status:re:(done|false)>')
def status_uuid(uuid, status):
    if osmose_common.remove_bug_uuid(uuid, status) == 0:
        return
    else:
        abort(410, "FAIL")


def _get_fix(db, fix_num, err_id=None, uuid=None):
    if err_id:
        sql = "SELECT fixes FROM marker WHERE id = %s"
        db.execute(sql, (err_id, ))
    else:
        sql = "SELECT fixes FROM marker WHERE uuid = %s"
        db.execute(sql, (uuid, ))

    fix = db.fetchone()

    if not fix:
        abort(410, "Fix is not present in database.")

    return fixes_default(fix[0])[fix_num]


@route('/api/0.2/error/<err_id:int>/fix')
@route('/api/0.2/error/<err_id:int>/fix/<fix_num:int>')
def fix_err_id(db, err_id, fix_num=0):
    return _fix(2, db, None, fix_num, _get_fix(db, fix_num, err_id=err_id))

@route('/api/0.3beta/issue/<uuid:uuid>/fix')
@route('/api/0.3beta/issue/<uuid:uuid>/fix/<fix_num:int>')
def fix_uuid(db, uuid, fix_num=0):
    return _fix(3, db, uuid, fix_num, _get_fix(db, fix_num, uuid=uuid))

def _fix(version, db, uuid, fix_num, fix):
    if fix:
      response.content_type = 'text/xml; charset=utf-8'
      for res in fix:
        if 'id' in res and res['id']:
            out = StringIO.StringIO()
            o = OsmSaxFixWriter(out, "UTF-8",
                                res['type'], res['id'],
                                res['create'], res['modify'], res['delete'])
            o.startDocument()

            data_type = {"N": "node", "W": "way", "R": "relation"}
            osm_read = utils.fetch_osm_data(data_type[res['type']], res['id'])
            osm_read.CopyTo(o)

            return out.getvalue()

        else:
            # create new object
            data = {}
            data["id"] = -1
            data["tag"] = {}
            for (k, v) in res['create'].iteritems():
                data["tag"][k] = v
            if version == 2:
                sql = "SELECT lat, lon FROM marker WHERE id = %s"
                db.execute(sql, (err_id, ))
            else:
                sql = "SELECT lat, lon FROM marker WHERE uuid = %s"
                db.execute(sql, (uuid, ))
            res2 = db.fetchone()
            data["lat"] = res2["lat"]
            data["lon"] = res2["lon"]

            if 'type' not in res or res['type'] == 'N':
                return OsmSax.NodeToXml(data, full=True)
            elif res['type'] == 'W':
                return OsmSax.WayToXml(data, full=True)
            elif res['type'] == 'R':
                return OsmSax.RelationToXml(data, full=True)

    else:
        abort(412, "Precondition Failed")
        #print "No issue found"


class OsmSaxFixWriter(OsmSax.OsmSaxWriter):

    def __init__(self,
                 out, enc,
                 elem_type, elem_id,
                 tags_create, tags_modify, tags_delete):
        OsmSax.OsmSaxWriter.__init__(self, out, enc)

        self.elem_type = elem_type
        self.elem_id = elem_id
        self.tags_create = tags_create
        self.tags_modify = tags_modify
        self.tags_delete = tags_delete

    def fix_tags(self, data):
        for k in self.tags_delete:
            if k in data["tag"]:
                del data["tag"][k]
        for (k, v) in self.tags_create.items():
            data["tag"][k] = v
        for (k, v) in self.tags_modify.items():
            data["tag"][k] = v
        data["action"] = "modify"
        return data

    def NodeCreate(self, data):
        if self.elem_type == "N" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.NodeCreate(self, data)

    def WayCreate(self, data):
        if self.elem_type == "W" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.WayCreate(self, data)

    def RelationCreate(self, data):
        if self.elem_type == "R" and self.elem_id == data["id"]:
            data = self.fix_tags(data)
        OsmSax.OsmSaxWriter.RelationCreate(self, data)
