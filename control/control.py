import os
import sys

from bottle import HTTPError, abort, post, request, response, route

from modules_legacy import utils

from . import update


@post("/send-update")
def send_update(db):
    analyser = request.params.get("analyser", default=None)
    country = request.params.get("country", default=None)
    code = request.params.get("code")
    upload = request.files.get("content", default=None)

    response.content_type = "text/plain; charset=utf-8"

    if not code or not upload:
        abort(401, "FAIL")

    db.execute(
        """
SELECT
    id
FROM
    sources
    JOIN sources_password ON
        sources.id = source_id
WHERE
    analyser = %(analyser)s AND
    country = %(country)s AND
    password = %(password)s
LIMIT 1
""",
        {"analyser": analyser, "country": country, "password": code},
    )

    res = db.fetchone()

    if not res and not os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        abort(403, "AUTH FAIL")
    if not res and os.environ.get("OSMOSE_UNLOCKED_UPDATE"):
        db.execute("SELECT COALESCE(MAX(id), 0) + 1 AS id FROM sources")
        source_id = db.fetchone()["id"]
        db.execute(
            "INSERT INTO sources(id, country, analyser) VALUES (%s, %s, %s)",
            (source_id, country, analyser),
        )
        db.execute(
            "INSERT INTO sources_password(source_id, password) VALUES(%s, %s)",
            (source_id, code),
        )
        db.connection.commit()
    else:
        source_id = res["id"]

    remote_ip = request.remote_addr

    try:
        (name, ext) = os.path.splitext(upload.filename)
        if ext not in (".bz2", ".gz", ".xml"):
            abort(406, "FAIL: File extension not allowed.")

        save_filename = os.path.join(utils.dir_results, upload.filename)
        upload.save(save_filename, overwrite=True)
        update.update(source_id, save_filename, remote_ip=remote_ip)
        os.unlink(save_filename)

    except update.OsmoseUpdateAlreadyDone:
        abort(409, "FAIL: Already up to date")

    except Exception:
        import traceback
        from io import StringIO

        s = StringIO()
        sys.stderr = s
        traceback.print_exc()
        sys.stderr = sys.__stderr__
        trace = s.getvalue()
        abort(500, trace.rstrip())

    return "OK"


def _status_object(db, t, source):
    db.execute(
        "SELECT string_agg(elem->>'id', ',') FROM (SELECT unnest(elems) AS elem FROM markers WHERE source_id=%s) AS t WHERE elem->>'type' = %s",
        (source, t),
    )
    s = db.fetchone()
    if s and s[0]:
        return list(map(int, s[0].split(",")))


@route("/status/<country>/<analyser>")
def status(db, country=None, analyser=None):
    if not country or not analyser:
        return HTTPError(400)

    objects = request.params.get("objects", default=False)

    db.execute(
        "SELECT timestamp, source_id, analyser_version FROM updates_last WHERE source_id = (SELECT id FROM sources WHERE analyser = %s AND country = %s)",
        (analyser, country),
    )
    r = db.fetchone()
    if r and r["timestamp"]:
        return {
            "version": 1,
            "timestamp": str(r["timestamp"].replace(tzinfo=None)),
            "analyser_version": str(r["analyser_version"] or ""),
            "nodes": _status_object(db, "N", r["source_id"])
            if objects is not False
            else None,
            "ways": _status_object(db, "W", r["source_id"])
            if objects is not False
            else None,
            "relations": _status_object(db, "R", r["source_id"])
            if objects is not False
            else None,
        }
    else:
        return HTTPError(404)
