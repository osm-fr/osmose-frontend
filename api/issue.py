import copy
import io
from typing import Literal, Union
from uuid import UUID

from bottle import abort, default_app, response, route

from modules import OsmSax, utils
from modules.query import fixes_default
from modules.utils import LangsNegociation

from .issue_utils import _expand_tags, _get, t2l

app_0_2 = default_app.pop()


Status = Literal["done", "false"]


def _remove_bug_err_id(db, error_id: int, status: Status):
    # find source
    db.execute(
        "SELECT uuid,source_id,class FROM markers WHERE uuid_to_bigint(uuid) = %s",
        (error_id,),
    )
    source_id = None
    for res in db.fetchall():
        uuid = res["uuid"]
        source_id = res["source_id"]
        class_id = res["class"]

    if not source_id:
        return -1

    db.execute("DELETE FROM markers_status WHERE uuid=%s", (uuid,))

    db.execute(
        """INSERT INTO markers_status
                        (source_id,item,class,elems,date,status,lat,lon,subtitle,uuid)
                      SELECT source_id,item,class,elems,NOW(),%s,
                             lat,lon,subtitle,uuid
                      FROM markers
                      WHERE uuid = %s
                      ON CONFLICT DO NOTHING""",
        (status, uuid),
    )

    db.execute("DELETE FROM markers WHERE uuid = %s", (uuid,))
    db.execute(
        "UPDATE markers_counts SET count = count - 1 WHERE source_id = %s AND class = %s;",
        (source_id, class_id),
    )
    db.connection.commit()

    return 0


def _remove_bug_uuid(db, uuid: UUID, status: Status):

    PgConn = utils.get_dbconn()
    db = PgConn.cursor()

    # find source
    db.execute("SELECT source_id,class FROM markers WHERE uuid = %s", (uuid,))
    source_id = None
    for res in db.fetchall():
        source_id = res["source_id"]
        class_id = res["class"]

    if not source_id:
        return -1

    db.execute("DELETE FROM markers_status WHERE uuid=%s", (uuid,))

    db.execute(
        """INSERT INTO markers_status
                        (source_id,item,class,elems,date,status,lat,lon,subtitle,uuid)
                      SELECT source_id,item,class,elems,NOW(),%s,
                             lat,lon,subtitle,uuid
                      FROM markers
                      WHERE uuid = %s
                      ON CONFLICT DO NOTHING""",
        (status, uuid),
    )

    db.execute("DELETE FROM markers WHERE uuid = %s", (uuid,))
    db.execute(
        "UPDATE markers_counts SET count = count - 1 WHERE source_id = %s AND class = %s;",
        (source_id, class_id),
    )
    db.connection.commit()

    return 0


@route("/issue/<uuid:uuid>/fresh_elems")
@route("/issue/<uuid:uuid>/fresh_elems/<fix_num:int>")
def fresh_elems_uuid(db, uuid: UUID, fix_num: Union[int, None] = None):
    data_type = {"N": "node", "W": "way", "R": "relation", "I": "infos"}

    marker = _get(db, uuid=uuid)
    if not marker:
        abort(410, "Id is not present in database.")

    def expand_tags(tags):
        t = []
        for (k, v) in tags.items():
            t.append({"k": k, "v": v})
        return t

    elems = {}
    for elem in marker["elems"]:
        if elem["type"]:
            fresh_elem = utils.fetch_osm_elem(data_type[elem["type"]], elem["id"])

            if fresh_elem and len(fresh_elem) > 0:
                tmp_elem = {
                    data_type[elem["type"]]: True,
                    "type": data_type[elem["type"]],
                    "id": elem["id"],
                    "version": fresh_elem["version"],
                    "tags": fresh_elem["tag"],
                }
                elems[data_type[elem["type"]] + str(elem["id"])] = tmp_elem

    ret = {
        "uuid": uuid,
        "elems": list(elems.values()),
    }

    if fix_num is not None:
        ret["fix"] = {}
        for res in marker["fixes"][fix_num]:
            tid = data_type[res["type"]] + str(res["id"])
            if tid in elems:
                fix_elem_tags = copy.copy(elems[tid]["tags"])
                for k in res["delete"]:
                    if k in fix_elem_tags:
                        del fix_elem_tags[k]
                for (k, v) in res["create"].items():
                    fix_elem_tags[k] = v
                for (k, v) in res["modify"].items():
                    fix_elem_tags[k] = v

                ret["fix"][tid] = fix_elem_tags

    for elem in ret["elems"]:
        elem["tags"] = expand_tags(elem["tags"])

    return ret


@app_0_2.route("/error/<err_id:int>")
def error_err_id(db, lang, err_id: int):
    return _error(2, db, lang, None, _get(db, err_id=err_id))


@route("/issue/<uuid:uuid>")
def error_uuid(db, langs: LangsNegociation, uuid: UUID):
    return _error(3, db, langs, uuid, _get(db, uuid=uuid))


def _error(version: int, db, langs: LangsNegociation, uuid: Union[UUID, None], marker):
    if not marker:
        abort(410, "Id is not present in database.")

    data_type = {"N": "node", "W": "way", "R": "relation", "I": "infos"}

    lat = str(marker["lat"])
    lon = str(marker["lon"])
    title = utils.i10n_select(marker["title"], langs)
    subtitle = utils.i10n_select(marker["subtitle"], langs)
    b_date = marker["timestamp"] or ""
    item = marker["item"] or 0
    classs = marker["class"] or 0

    elems = []
    for elem in marker["elems"] or []:
        if elem["type"]:
            tags = elem.get("tags", {})
            tmp_elem = {
                data_type[elem["type"]]: True,
                "type": data_type[elem["type"]],
                "id": elem["id"],
                "tags": _expand_tags(tags, t2l.checkTags(tags)),
                "fixes": [],
            }
            for fix_index, fix_group in enumerate(marker["fixes"] or []):
                for fix in fix_group:
                    if (
                        fix["type"]
                        and fix["type"] == elem["type"]
                        and fix["id"] == elem["id"]
                    ):
                        tmp_elem["fixes"].append(
                            {
                                "num": fix_index,
                                "add": _expand_tags(
                                    fix["create"], t2l.checkTags(fix["create"])
                                ),
                                "mod": _expand_tags(
                                    fix["modify"], t2l.checkTags(fix["modify"])
                                ),
                                "del": _expand_tags(fix["delete"], {}, True),
                            }
                        )
            elems.append(tmp_elem)

    new_elems = []
    for fix_index, fix_group in enumerate(marker["fixes"] or []):
        for fix in fix_group:
            if fix["type"]:
                found = False
                for e in elems:
                    if e["type"] == data_type[fix["type"]] and e["id"] == fix["id"]:

                        found = True
                        break
                if not found:
                    new_elems.append(
                        {
                            "num": fix_index,
                            "add": _expand_tags(
                                fix["create"], t2l.checkTags(fix["create"])
                            ),
                            "mod": _expand_tags(
                                fix["modify"], t2l.checkTags(fix["modify"])
                            ),
                            "del": _expand_tags(fix["delete"], {}, True),
                        }
                    )

    if version == 2:
        return {
            "lat": lat,
            "lon": lon,
            "minlat": float(lat) - 0.002,
            "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002,
            "maxlon": float(lon) + 0.002,
            "error_id": marker["id"],
            "title": title and title["auto"],
            "subtitle": subtitle and subtitle["auto"],
            "b_date": b_date.strftime("%Y-%m-%d"),
            "item": item,
            "class": classs,
            "elems": elems,
            "new_elems": new_elems,
            "elems_id": ",".join(
                map(lambda elem: elem["type_long"] + str(elem["id"]), marker["elems"])
            ),
            "url_help": "",  # Keep for retro compatibility
        }
    else:
        return {
            "lat": lat,
            "lon": lon,
            "minlat": float(lat) - 0.002,
            "maxlat": float(lat) + 0.002,
            "minlon": float(lon) - 0.002,
            "maxlon": float(lon) + 0.002,
            "uuid": uuid,
            "title": title,
            "subtitle": subtitle,
            "b_date": b_date.strftime("%Y-%m-%d"),
            "item": item,
            "class": classs,
            "elems": elems,
            "new_elems": new_elems,
        }


@app_0_2.route("/error/<err_id:int>/<status:re:(done|false)>")
def status_err_id(db, err_id: int, status: Status):
    if _remove_bug_err_id(db, err_id, status) == 0:
        return
    else:
        abort(410, "FAIL")


@route("/issue/<uuid:uuid>/<status:re:(done|false)>")
def status_uuid(db, uuid: UUID, status: Status):
    if _remove_bug_uuid(db, uuid, status) == 0:
        return
    else:
        abort(410, "FAIL")


def _get_fix(
    db, fix_num: int, err_id: Union[int, None] = None, uuid: Union[UUID, None] = None
):
    if err_id:
        sql = "SELECT fixes FROM markers WHERE id = %s"
        db.execute(sql, (err_id,))
    else:
        sql = "SELECT fixes FROM markers WHERE uuid = %s"
        db.execute(sql, (uuid,))

    fix = db.fetchone()

    if not fix:
        abort(410, "Fix is not present in database.")

    return fixes_default(fix[0])[fix_num]


@app_0_2.route("/error/<err_id:int>/fix")
@app_0_2.route("/error/<err_id:int>/fix/<fix_num:int>")
def fix_err_id(db, err_id: int, fix_num: int = 0):
    return _fix(2, db, None, fix_num, _get_fix(db, fix_num, err_id=err_id))


@route("/issue/<uuid:uuid>/fix")
@route("/issue/<uuid:uuid>/fix/<fix_num:int>")
def fix_uuid(db, uuid: UUID, fix_num: int = 0):
    return _fix(3, db, uuid, fix_num, _get_fix(db, fix_num, uuid=uuid))


def _fix(version: int, db, uuid: Union[UUID, None], fix_num: int, fix):
    if fix:
        response.content_type = "text/xml; charset=utf-8"
        for res in fix:
            if "id" in res and res["id"]:
                out = io.StringIO()
                o = OsmSaxFixWriter(
                    out,
                    "UTF-8",
                    res["type"],
                    res["id"],
                    res["create"],
                    res["modify"],
                    res["delete"],
                )
                o.startDocument()

                data_type = {"N": "node", "W": "way", "R": "relation"}
                osm_read = utils.fetch_osm_data(data_type[res["type"]], res["id"])
                osm_read.CopyTo(o)

                return out.getvalue()

            else:
                # create new object
                data = {}
                data["id"] = -1
                data["tag"] = {}
                for (k, v) in res["create"].items():
                    data["tag"][k] = v
                if version == 2:
                    sql = "SELECT lat, lon FROM markers WHERE id = %s"
                    db.execute(sql, (err_id,))
                else:
                    sql = "SELECT lat, lon FROM markers WHERE uuid = %s"
                    db.execute(sql, (uuid,))
                res2 = db.fetchone()
                data["lat"] = res2["lat"]
                data["lon"] = res2["lon"]
                data["action"] = "modify"  # Even for creation action is 'modify'

                if "type" not in res or res["type"] == "N":
                    return OsmSax.NodeToXml(data, full=True)
                elif res["type"] == "W":
                    return OsmSax.WayToXml(data, full=True)
                elif res["type"] == "R":
                    return OsmSax.RelationToXml(data, full=True)

    else:
        abort(412, "Precondition Failed")
        # print "No issue found"


class OsmSaxFixWriter(OsmSax.OsmSaxWriter):
    def __init__(
        self, out, enc, elem_type, elem_id, tags_create, tags_modify, tags_delete
    ):
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


default_app.push(app_0_2)
