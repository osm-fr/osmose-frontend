import io

from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Request

from modules import OsmSax, utils
from modules.dependencies import database

from .tool import oauth

router = APIRouter()


@router.post("/editor/save")
async def save(
    request: Request,
    db: Connection = Depends(database.db),
):
    json = await request.json()
    if "tag" not in json:
        raise HTTPException(status_code=422)

    # Changeset tags
    tags = json["tag"]
    if "comment" not in tags or tags["comment"].strip() == "":
        tags["comment"] = "Fixed with Osmose"
    if "source" not in tags or tags["source"].strip() == "":
        tags["source"] = "Osmose"
    if "type" not in tags or tags["type"].strip() == "":
        tags["type"] = "fix"
    tags["created_by"] = "Osmose Editor"

    reuse_changeset = json.get("reuse_changeset", True) is not False

    # Get an open changeset
    changeset = request.session.get("changeset")
    if changeset and not reuse_changeset:
        try:
            _changeset_close(request.session["oauth_tokens"], changeset)
        except Exception:
            pass
        changeset = None
        del request.session["changeset"]
        request.session.save()
    elif changeset:
        try:
            _changeset_update(request.session["oauth_tokens"], changeset, tags)
        except Exception:
            changeset = None
            request.session["changeset"] = changeset
            request.session.save()

    if not changeset:
        changeset = _changeset_create(request.session["oauth_tokens"], tags)
        request.session["changeset"] = changeset
        request.session.save()

    # OsmChange
    out = io.StringIO()
    o = OsmSax.OsmSaxWriter(out, "UTF-8")
    o.startDocument()
    o.startElement("osmChange", {"version": "0.6", "generator": "OsmSax"})

    methode = {"node": o.NodeCreate, "way": o.WayCreate, "relation": o.RelationCreate}
    for action in ("modify", "delete"):
        if action in json and len(json[action]) > 0:
            o.startElement(action, {})
            for e in json[action]:
                try:
                    ee = utils.fetch_osm_elem(e["type"], e["id"])
                except Exception:
                    ee = None
                if ee and ee["version"] == int(e["version"]):
                    ee["changeset"] = changeset
                    ee["tag"] = e["tags"]
                    methode[e["type"]](ee)
                else:
                    # FIXME reject
                    pass
            o.endElement(action)

    o.endElement("osmChange")
    osmchange = out.getvalue()

    # Fire the changeset
    _changeset_upload(request.session["oauth_tokens"], changeset, osmchange)


def _osm_changeset(tags, id="0"):
    out = io.StringIO()
    o = OsmSax.OsmSaxWriter(out, "UTF-8")
    o.startDocument()
    o.startElement("osm", {"version": "0.6", "generator": "Osmose"})
    o.startElement("changeset", {"id": id, "open": "false"})
    for (k, v) in tags.items():
        o.Element("tag", {"k": k, "v": v})
    o.endElement("changeset")
    o.endElement("osm")

    return out.getvalue()


def _changeset_create(oauth_tokens, tags):
    changeset = oauth.put(
        oauth_tokens,
        utils.remote_url_write + "api/0.6/changeset/create",
        _osm_changeset(tags),
    )
    return changeset


def _changeset_update(oauth_tokens, id, tags):
    oauth.put(
        oauth_tokens,
        utils.remote_url_write + "api/0.6/changeset/" + id,
        _osm_changeset(tags, id=id),
    )


def _changeset_close(oauth_tokens, id):
    oauth.put(
        oauth_tokens,
        utils.remote_url_write + "api/0.6/changeset/" + id + "/close",
    )


def _changeset_upload(oauth_tokens, id, osmchange):
    oauth.post(
        oauth_tokens,
        utils.remote_url_write + "api/0.6/changeset/" + id + "/upload",
        osmchange,
    )
