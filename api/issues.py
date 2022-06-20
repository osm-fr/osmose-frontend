from collections import OrderedDict
from itertools import groupby

from bottle import default_app, response, route

from modules import query, utils
from modules.params import Params

app_0_2 = default_app.pop()


@app_0_2.route("/errors")
def errors(db, lang):
    params = Params()
    results = query._gets(db, params)
    out = OrderedDict()

    if not params.full:
        out["description"] = ["lat", "lon", "error_id", "item"]
    else:
        out["description"] = [
            "lat",
            "lon",
            "error_id",
            "item",
            "source",
            "class",
            "elems",
            "subclass",
            "subtitle",
            "title",
            "level",
            "update",
            "username",
        ]
    out["errors"] = []

    for res in results:
        lat = res["lat"]
        lon = res["lon"]
        error_id = res["id"]
        item = res["item"] or 0

        if not params.full:
            out["errors"].append([str(lat), str(lon), str(error_id), str(item)])
        else:
            source = res["source_id"]
            classs = res["class"]
            elems = "_".join(
                map(
                    lambda elem: {"N": "node", "W": "way", "R": "relation"}[
                        elem["type"]
                    ]
                    + str(elem["id"]),
                    res["elems"] or [],
                )
            )
            subclass = 0

            subtitle = utils.i10n_select(res["subtitle"], lang)
            subtitle = subtitle and subtitle["auto"] or ""

            title = utils.i10n_select(res["title"], lang)
            title = title and title["auto"] or ""

            level = res["level"]
            update = res["timestamp"]
            username = ",".join(
                map(
                    lambda elem: "username" in elem and elem["username"] or "",
                    res["elems"] or [],
                )
            )
            out["errors"].append(
                [
                    str(lat),
                    str(lon),
                    str(error_id),
                    str(item),
                    str(source),
                    str(classs),
                    str(elems),
                    str(subclass),
                    subtitle,
                    title,
                    str(level),
                    str(update),
                    username,
                ]
            )

    return out


@route("/issues")
@route("/issues.<format:ext>")
def errors(db, langs, format=None):
    params = Params(max_limit=10000)
    results = query._gets(db, params)

    out = []
    for res in results:
        i = {
            "lat": float(res["lat"]),
            "lon": float(res["lon"]),
            "id": res["uuid"],
            "item": str(res["item"]),
        }
        if params.full:
            i.update(
                {
                    "lat": float(res["lat"]),
                    "lon": float(res["lon"]),
                    "id": res["uuid"],
                    "item": str(res["item"]),
                    "source": res["source_id"],
                    "class": res["class"],
                    "subtitle": utils.i10n_select(res["subtitle"], langs),
                    "title": utils.i10n_select(res["title"], langs),
                    "level": res["level"],
                    "update": str(res["timestamp"]),
                    "usernames": list(
                        map(
                            lambda elem: "username" in elem and elem["username"] or "",
                            res["elems"] or [],
                        )
                    ),
                    "osm_ids": dict(
                        map(
                            lambda k_g: [
                                {"N": "nodes", "W": "ways", "R": "relations"}[k_g[0]],
                                list(map(lambda g: g["id"], k_g[1])),
                            ],
                            groupby(
                                sorted(res["elems"] or [], key=lambda e: e["type"]),
                                lambda e: e["type"],
                            ),
                        )
                    ),
                }
            )
        out.append(i)

    if format != "geojson":
        return {"issues": out}
    else:
        response.content_type = "application/vnd.geo+json"
        return {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [properties["lon"], properties["lat"]],
                    },
                    "properties": {
                        k: v for k, v in properties.items() if k not in ("lon", "lat")
                    },
                }
                for properties in out
            ],
        }


default_app.push(app_0_2)
