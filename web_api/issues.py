import io
import traceback
from collections import defaultdict
from typing import Dict

from asyncpg import Connection
from fastapi import APIRouter, Depends, Request, Response

from modules import query, query_meta, utils
from modules.dependencies import commons_params, database, langs
from modules.utils import LangsNegociation, i10n_select_auto

from . import errors_graph

router = APIRouter()


@router.get("/issues/graph.png")
@router.get("/issues/graph.svg")
@router.get("/issues/graph.pdf")
@router.get("/issues/graph.csv")
@router.get("/issues/graph.json")
async def graph(
    request: Request,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
):
    try:
        format = request.url.path.split(".", -1)[1]
        data = await errors_graph.make_plt(db, params, format)
        media_type = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "csv": "text/csv",
            "json": "application/json",
        }[format]
        return Response(content=data, media_type=media_type)
    except Exception:
        out = io.StringIO()
        traceback.print_exc(file=out)
        return Response(content=out.getvalue() + "\n", media_type="text/plain")


@router.get("/issues/open.json")
@router.get("/issues/done.json")
@router.get("/issues/false-positive.json")
async def index(
    request: Request,
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
    langs: LangsNegociation = Depends(langs.langs),
):
    if "false-positive" in request.url.path:
        gen = "false"
    elif "done" in request.url.path:
        gen = "done"
    else:
        gen = "open"

    items = await query_meta._items_menu(db, langs)
    countries = await query_meta._countries(db)

    if params.item:
        params.limit = None
        errors_groups = await query._count(
            db,
            params,
            [
                "markers_counts.item",
                "markers.source_id",
                "markers.class",
                "sources.country",
                "sources.analyser",
                "updates_last.timestamp",
            ],
            ["items", "class"],
            [
                "min(items.menu::text)::jsonb AS menu",
                "min(class.title::text)::jsonb AS title",
            ],
        )

        total = 0
        for res in errors_groups:
            res["title"] = i10n_select_auto(res["title"], langs)
            res["menu"] = i10n_select_auto(res["menu"], langs)
            if res["count"] != -1:
                total += res["count"]
    else:
        errors_groups = []
        total = 0

    if gen in ("false", "done"):
        opt_date = "date"
    else:
        opt_date = None

    errors_groups = list(map(dict, errors_groups))
    for res in errors_groups:
        res["timestamp"] = str(res["timestamp"])
    return dict(
        countries=countries,
        items=items,
        errors_groups=errors_groups,
        total=total,
        gen=gen,
        opt_date=opt_date,
        website=utils.website,
        main_website=utils.main_website,
        remote_url_read=utils.remote_url_read,
    )


@router.get("/issues/matrix.json")
async def matrix(
    db: Connection = Depends(database.db),
    params=Depends(commons_params.params),
):
    errors_groups = await query._count(
        db,
        params,
        [
            "markers.item",
            "markers.class",
            "sources.country",
            "items.menu->'en' AS menu",
        ],
    )
    analysers: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    analysers_sum: Dict[str, int] = defaultdict(int)
    countries_sum: Dict[str, int] = defaultdict(int)
    total = 0
    for row in errors_groups:
        analyser = "{}/{} {}".format(row["item"], row["class"], row["menu"])
        count = row["count"]
        analysers[analyser][row["country"]] += count
        analysers_sum[analyser] += count
        countries_sum[row["country"]] += count
        total += count

    return dict(
        total=total,
        countries_sum=countries_sum,
        analysers_sum=analysers_sum,
        analysers=analysers,
    )
