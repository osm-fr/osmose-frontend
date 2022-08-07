import json
from collections import OrderedDict
from itertools import groupby

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import RedirectResponse

from modules import query, query_meta, utils
from modules.dependencies import commons_params, database, formats, langs
from modules.utils import LangsNegociation, i10n_select_auto

from .issues_utils import gpx, kml, rss

router = APIRouter()


#  TODO use i18n
def _(s):
    return s


@router.get("/0.2/errors", tags=["0.2"])
async def errors(
    request: Request,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
):
    results = await query._gets(db, params)
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

            subtitle = utils.i10n_select(res["subtitle"], ["en"])
            subtitle = subtitle and subtitle["auto"] or ""

            title = utils.i10n_select(res["title"], ["en"])
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


@router.get("/0.3/issues", tags=["issues"])
@router.get("/0.3/issues.json", tags=["issues"])
async def issues(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    params=Depends(commons_params.params),
):
    params.limit = min(params.limit, 10000)
    results = await query._gets(db, params)

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

    return {"issues": out}


@router.get("/0.3/issues.josm", tags=["issues"])
async def issues_josm(
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
):
    params.full = True
    params.limit = min(params.limit, 10000)
    results = await query._gets(db, params)

    objects = set(
        sum(
            map(
                lambda error: list(
                    map(
                        lambda elem: elem["type"].lower() + str(elem["id"]),
                        error["elems"] or [],
                    )
                ),
                results,
            ),
            [],
        )
    )
    return RedirectResponse(
        url=f"http://localhost:8111/load_object?objects={','.join(objects)}"
    )


@router.get("/0.3/issues.{format}", tags=["issues"])
async def issues_format(
    request: Request,
    db: Connection = Depends(database.db),
    langs: LangsNegociation = Depends(langs.langs),
    format: str = Depends(formats.formats("geojson", "rss", "gpx", "kml")),
    params=Depends(commons_params.params),
):
    if params.status == "false":
        title = _("False positives")
    elif params.status == "done":
        title = _("Fixed issues")
    else:
        title = _("Open issues")

    items = await query_meta._items_menu(db, langs)
    for res in items:
        if params.item == str(res["item"]):
            title += " - " + i10n_select_auto(res["menu"], langs)

    params.full = True
    params.limit = min(params.limit, 10000)
    issues = await query._gets(db, params)

    for issue in issues:
        issue["subtitle"] = i10n_select_auto(issue["subtitle"], langs)
        issue["title"] = i10n_select_auto(issue["title"], langs)
        issue["menu"] = i10n_select_auto(issue["menu"], langs)

    if format == "rss":
        return Response(
            media_type="application/rss+xml",
            content=rss(
                title=title,
                website=utils.website,
                langs=langs,
                params=params,
                query=str(request.query_params),
                main_website=utils.main_website,
                remote_url_read=utils.remote_url_read,
                issues=issues,
            ),
        )
    elif format == "gpx":
        return Response(
            media_type="application/gpx+xml",
            content=gpx(
                title=title,
                website=utils.website,
                langs=langs,
                params=params,
                query=str(request.query_params),
                main_website=utils.main_website,
                remote_url_read=utils.remote_url_read,
                issues=issues,
            ),
        )
    elif format == "kml":
        return Response(
            media_type="application/vnd.google-earth.kml+xml",
            content=kml(
                title=title,
                website=utils.website,
                langs=langs,
                params=params,
                query=str(request.query_params),
                main_website=utils.main_website,
                remote_url_read=utils.remote_url_read,
                issues=issues,
            ),
        )
    else:
        return Response(
            media_type="application/vnd.geo+json",
            content=json.dumps(
                jsonable_encoder(
                    {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [
                                        properties["lon"],
                                        properties["lat"],
                                    ],
                                },
                                "properties": {
                                    k: v
                                    for k, v in properties.items()
                                    if k not in ("id", "lon", "lat")
                                },
                            }
                            for properties in issues
                        ],
                    }
                )
            ),
        )
