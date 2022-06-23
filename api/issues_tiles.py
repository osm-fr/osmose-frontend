import math
from typing import Literal

import mapbox_vector_tile
from bottle import HTTPError, HTTPResponse, default_app, response, route
from shapely.geometry import Point, Polygon

from modules import query, tiles
from modules.params import Params

app_0_2 = default_app.pop()


def _errors_mvt(
    results,
    z: int,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    limit: int,
):
    if not results or len(results) == 0:
        return None
    else:
        limit_feature = []
        if len(results) == limit and z < 18:
            limit_feature = [
                {
                    "name": "limit",
                    "features": [
                        {
                            "geometry": Point(
                                (min_lon + max_lon) / 2, (min_lat + max_lat) / 2
                            )
                        }
                    ],
                }
            ]

        issues_features = []
        for res in sorted(results, key=lambda res: -res["lat"]):
            issues_features.append(
                {
                    "geometry": Point(res["lon"], res["lat"]),
                    "properties": {
                        "uuid": res["uuid"],
                        "item": res["item"] or 0,
                        "class": res["class"] or 0,
                    },
                }
            )

        return mapbox_vector_tile.encode(
            [{"name": "issues", "features": issues_features}] + limit_feature,
            quantize_bounds=(min_lon, min_lat, max_lon, max_lat),
        )


def _errors_geojson(
    results,
    z: int,
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    limit: int,
):
    if not results or len(results) == 0:
        return None
    else:
        issues_features = []
        for res in sorted(results, key=lambda res: -res["lat"]):
            issues_features.append(
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(res["lon"]), float(res["lat"])],
                    },
                    "properties": {
                        "uuid": res["uuid"],
                        "item": res["item"] or 0,
                        "class": res["class"] or 0,
                    },
                }
            )

        features_collection = {
            "type": "FeatureCollection",
            "features": issues_features,
        }

        if len(results) == limit and z < 18:
            features_collection["properties"] = {"limit": limit}

        return features_collection


@route("/issues/<z:int>/<x:int>/<y:int>.heat.mvt")
def heat(db, z: int, x: int, y: int):
    COUNT = 32

    lon1, lat2 = tiles.tile2lonlat(x, y, z)
    lon2, lat1 = tiles.tile2lonlat(x + 1, y + 1, z)

    params = Params()
    items = query._build_where_item(params.item, "items")
    params.tilex = x
    params.tiley = y
    params.zoom = z

    if params.zoom > 18:
        return

    db.execute(
        """
SELECT
    SUM((SELECT SUM(t) FROM UNNEST(number) t))
FROM
    items
WHERE
"""
        + items
    )
    limit = db.fetchone()
    if limit and limit[0]:
        limit = float(limit[0])
    else:
        return HTTPError(404)

    join, where = query._build_param(
        db,
        None,
        params.source,
        params.item,
        params.level,
        params.users,
        params.classs,
        params.country,
        params.useDevItem,
        params.status,
        params.tags,
        params.fixable,
        tilex=params.tilex,
        tiley=params.tiley,
        zoom=params.zoom,
    )
    join = join.replace("%", "%%")
    where = where.replace("%", "%%")

    sql = (
        """
SELECT
    COUNT(*),
    ((lon-%(lon1)s) * %(count)s / (%(lon2)s-%(lon1)s) + 0.5)::int AS latn,
    ((lat-%(lat1)s) * %(count)s / (%(lat2)s-%(lat1)s) + 0.5)::int AS lonn,
    mode() WITHIN GROUP (ORDER BY items.marker_color) AS color
FROM
"""
        + join
        + """
WHERE
"""
        + where
        + """
GROUP BY
    latn,
    lonn
"""
    )
    db.execute(
        sql, {"lon1": lon1, "lat1": lat1, "lon2": lon2, "lat2": lat2, "count": COUNT}
    )

    features = []
    for row in db.fetchall():
        count, x, y, color = row
        count = max(
            int(
                math.log(count)
                / math.log(limit / ((z - 4 + 1 + math.sqrt(COUNT)) ** 2))
                * 255
            ),
            1 if count > 0 else 0,
        )
        if count > 0:
            count = 255 if count > 255 else count
            features.append(
                {
                    "geometry": Polygon(
                        [(x, y), (x - 1, y), (x - 1, y - 1), (x, y - 1)]
                    ),
                    "properties": {"color": int(color[1:], 16), "count": count},
                }
            )

    response.content_type = "application/vnd.mapbox-vector-tile"
    return mapbox_vector_tile.encode(
        [{"name": "issues", "features": features}], extents=COUNT
    )


TileFormat = Literal["mvt", "geojson"]


@route("/issues/<z:int>/<x:int>/<y:int>.<format:ext>")
def issues_mvt(db, z: int, x: int, y: int, format: TileFormat):
    lon1, lat2 = tiles.tile2lonlat(x, y, z)
    lon2, lat1 = tiles.tile2lonlat(x + 1, y + 1, z)

    params = Params(max_limit=50 if z > 18 else 10000)
    params.tilex = x
    params.tiley = y
    params.zoom = z
    params.full = False

    if params.zoom > 18:
        return
    if (not params.users) and (not params.source) and (params.zoom < 7):
        return

    results = query._gets(db, params) if z >= 7 else None

    if format == "mvt":
        tile = _errors_mvt(results, z, lon1, lat1, lon2, lat2, params.limit)
        if tile:
            response.content_type = "application/vnd.mapbox-vector-tile"
            return tile
        else:
            return HTTPResponse(
                status=204, headers={"Access-Control-Allow-Origin": "*"}
            )
    elif format in ("geojson", "json"):  # Fall back to GeoJSON
        tile = _errors_geojson(results, z, lon1, lat1, lon2, lat2, params.limit)
        if tile:
            response.content_type = "application/vnd.geo+json"
            return tile
        else:
            return []
    else:
        return HTTPError(404)


default_app.push(app_0_2)
