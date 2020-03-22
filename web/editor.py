#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2014                                      ##
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

import StringIO

from bottle import post, request, abort
from tools import OsmSax

from tools import utils
from tool import oauth


@post('/editor/save')
def save(db, lang):
    json = request.json
    if not json.has_key('tag'):
        abort(422)

    # Changeset tags
    tags = json['tag']
    if not tags.has_key('comment') or tags['comment'].strip() == '':
        tags['comment'] = u'Fix with Osmose'
    if not tags.has_key('source') or tags['source'].strip() == '':
        tags['source'] = u'Osmose'
    if not tags.has_key('type') or tags['type'].strip() == '':
        tags['type'] = u'fix'
    tags['created_by'] = u'Osmose Editor'

    reuse_changeset = json.get('reuse_changeset', True) != False

    # Get an open changeset
    changeset = request.session.get('changeset')
    if changeset and not reuse_changeset:
        try:
            _changeset_close(changeset)
        except:
            pass
        changeset = None
        del request.session['changeset']
        request.session.save()
    elif changeset:
        try:
            _changeset_update(changeset, tags)
        except:
            changeset = None
            request.session['changeset'] = changeset
            request.session.save()

    if not changeset:
        changeset = _changeset_create(tags)
        request.session['changeset'] = changeset
        request.session.save()

    # OsmChange
    out = StringIO.StringIO()
    o = OsmSax.OsmSaxWriter(out, "UTF-8")
    o.startDocument()
    o.startElement('osmChange', {"version": "0.6", "generator": "OsmSax"})

    methode = {'node': o.NodeCreate, 'way': o.WayCreate, 'relation': o.RelationCreate}
    for action in ('modify', 'delete'):
        if json.has_key(action) and len(json[action]) > 0:
            o.startElement(action, {})
            for (k, e) in json[action].items():
                try:
                    ee = utils.fetch_osm_elem(e['type'], e["id"])
                except:
                    ee = None
                if ee and ee['version'] == int(e['version']):
                    ee[u'changeset'] = changeset
                    ee['tag'] = e['tag']
                    methode[e['type']](ee)
                else:
                    # FIXME reject
                    pass
            o.endElement(action)

    o.endElement('osmChange')
    osmchange = out.getvalue()

    # Fire the changeset
    _changeset_upload(changeset, osmchange)


def _osm_changeset(tags, id='0'):
    out = StringIO.StringIO()
    o = OsmSax.OsmSaxWriter(out, "UTF-8")
    o.startDocument()
    o.startElement('osm', {"version": "0.6", "generator": u"Osmose"})
    o.startElement('changeset', {"id": id, "open": "false"})
    for (k,v) in tags.items():
        o.Element('tag', {'k': k, 'v': v})
    o.endElement('changeset')
    o.endElement('osm')

    return out.getvalue()


def _changeset_create(tags):
    changeset = oauth.put(request.session['oauth_tokens'],
        utils.remote_url_write + 'api/0.6/changeset/create',
        _osm_changeset(tags))
    return changeset


def _changeset_update(id, tags):
    changeset = oauth.put(request.session['oauth_tokens'],
        utils.remote_url_write + 'api/0.6/changeset/' + id,
        _osm_changeset(tags, id=id))


def _changeset_close(id):
    changeset = oauth.put(request.session['oauth_tokens'],
        utils.remote_url_write + 'api/0.6/changeset/' + id + '/close')


def _changeset_upload(id, osmchange):
    changeset = oauth.post(request.session['oauth_tokens'],
        utils.remote_url_write + 'api/0.6/changeset/' + id + '/upload',
        osmchange)
