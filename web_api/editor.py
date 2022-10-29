import io

from bottle import post, request, abort
from modules_legacy import OsmSax

from modules_legacy import utils
from .tool import oauth


@post('/editor/save')
def save(db, lang):
    json = request.json
    if 'tag' not in json:
        abort(422)

    # Changeset tags
    tags = json['tag']
    if 'comment' not in tags or tags['comment'].strip() == '':
        tags['comment'] = u'Fixed with Osmose'
    if 'source' not in tags or tags['source'].strip() == '':
        tags['source'] = u'Osmose'
    if 'type' not in tags or tags['type'].strip() == '':
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
    out = io.StringIO()
    o = OsmSax.OsmSaxWriter(out, "UTF-8")
    o.startDocument()
    o.startElement('osmChange', {"version": "0.6", "generator": "OsmSax"})

    methode = {'node': o.NodeCreate, 'way': o.WayCreate, 'relation': o.RelationCreate}
    for action in ('modify', 'delete'):
        if action in json and len(json[action]) > 0:
            o.startElement(action, {})
            for e in json[action]:
                try:
                    ee = utils.fetch_osm_elem(e['type'], e["id"])
                except:
                    ee = None
                if ee and ee['version'] == int(e['version']):
                    ee[u'changeset'] = changeset
                    ee['tag'] = e['tags']
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
    out = io.StringIO()
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
