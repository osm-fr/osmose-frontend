from uuid import UUID

from bottle import abort, default_app, delete, route

from modules import utils
from modules.utils import LangsNegociation

from .false_positive_utils import _get

app_0_2 = default_app.pop()


@route("/false-positive/<uuid:uuid>")
def fp_uuid(db, langs: LangsNegociation, uuid: UUID):
    marker, columns = _get(db, "false", uuid=uuid)
    if not marker:
        abort(410, "Id is not present in database.")

    lat = str(marker["lat"])
    lon = str(marker["lon"])
    title = utils.i10n_select(marker["title"], langs)
    subtitle = utils.i10n_select(marker["subtitle"], langs)
    item = marker["item"] or 0
    date = marker["date"].isoformat() or 0

    return {
        "lat": lat,
        "lon": lon,
        "minlat": float(lat) - 0.002,
        "maxlat": float(lat) + 0.002,
        "minlon": float(lon) - 0.002,
        "maxlon": float(lon) + 0.002,
        "id": uuid,
        "title": title,
        "subtitle": subtitle,
        "b_date": None,  # Keep for retro compatibility
        "item": item,
        "date": date,
    }


@delete("/false-positive/<uuid:uuid>")
def fp_delete_uuid(db, uuid: UUID):
    db.execute(
        "SELECT uuid FROM markers_status WHERE status = %s AND uuid = %s",
        ("false", uuid),
    )
    m = db.fetchone()
    if not m:
        abort(410, "FAIL")

    db.execute(
        "DELETE FROM markers_status WHERE status = %s AND uuid = %s", ("false", uuid)
    )
    db.connection.commit()

    return


default_app.push(app_0_2)
