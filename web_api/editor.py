import io
from typing import Dict, Optional
from uuid import UUID

import requests
from asyncpg import Connection
from fastapi import APIRouter, Depends, HTTPException, Request

from modules import OsmSax, utils
from modules.dependencies import database

from .tool.session import SessionData, backend, cookie, verifier

router = APIRouter()


@router.post("/editor/save")
async def save(
    request: Request,
    db: Connection = Depends(database.db),
    session_id: UUID = Depends(cookie),
    session_data: Optional[SessionData] = Depends(verifier),
) -> None:
    if not session_data or not session_data.oauth2_token:
        raise HTTPException(status_code=401)

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
    changeset = session_data.changeset
    if changeset and not reuse_changeset:
        try:
            _changeset_close(session_data.oauth2_token, changeset)
        except Exception:
            pass
        changeset = None
        session_data.changeset = None
        await backend.update(session_id, session_data)
    elif changeset:
        try:
            _changeset_update(session_data.oauth2_token, changeset, tags)
        except Exception:
            changeset = None
            session_data.changeset = changeset
            await backend.update(session_id, session_data)

    if not changeset:
        changeset = _changeset_create(session_data.oauth2_token, tags)
        session_data.changeset = changeset
        await backend.update(session_id, session_data)

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
    _changeset_upload(session_data.oauth2_token, changeset, osmchange)


def _osm_changeset(tags, id: str = "0") -> str:
    out = io.StringIO()
    o = OsmSax.OsmSaxWriter(out, "UTF-8")
    o.startDocument()
    o.startElement("osm", {"version": "0.6", "generator": "Osmose"})
    o.startElement("changeset", {"id": id, "open": "false"})
    for k, v in tags.items():
        o.Element("tag", {"k": k, "v": v})
    o.endElement("changeset")
    o.endElement("osm")

    return out.getvalue()


def _changeset_create(oauth2_token: str, tags: Dict[str, str]) -> str:
    request = requests.put(
        utils.remote_url_write + "api/0.6/changeset/create",
        data=_osm_changeset(tags),
        headers={"Authorization": f"Bearer {oauth2_token}"},
    )
    request.raise_for_status()
    return request.text


def _changeset_update(oauth2_token: str, id: str, tags: Dict[str, str]) -> None:
    request = requests.put(
        utils.remote_url_write + "api/0.6/changeset/" + id,
        data=_osm_changeset(tags, id=id),
        headers={"Authorization": f"Bearer {oauth2_token}"},
    )
    request.raise_for_status()


def _changeset_close(oauth2_token: str, id: str) -> None:
    request = requests.put(
        utils.remote_url_write + "api/0.6/changeset/" + id + "/close",
        headers={"Authorization": f"Bearer {oauth2_token}"},
    )
    request.raise_for_status()


def _changeset_upload(oauth2_token: str, id: str, osmchange) -> None:
    request = requests.post(
        utils.remote_url_write + "api/0.6/changeset/" + id + "/upload",
        data=osmchange,
        headers={"Authorization": f"Bearer {oauth2_token}"},
    )
    request.raise_for_status()
