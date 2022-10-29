import io
import re
from collections import defaultdict

from bottle import redirect, request, response, route

from modules_legacy import query, query_meta, utils
from modules_legacy.params import Params
from modules_legacy.utils import i10n_select_auto

from . import errors_graph


@route("/issues/graph.<format:ext>")
def graph(db, format="png"):
    try:
        data = errors_graph.make_plt(db, Params(), format)
        response.content_type = {
            "png": "image/png",
            "svg": "image/svg+xml",
            "pdf": "application/pdf",
            "csv": "text/csv",
            "json": "application/json",
        }[format]
        return data
    except Exception as e:
        response.content_type = "text/plain"
        import traceback

        out = io.StringIO()
        traceback.print_exc(file=out)
        return out.getvalue() + "\n"


@route("/issues/open.json")
@route("/issues/done.json")
@route("/issues/false-positive.json")
def index(db, lang):
    if "false-positive" in request.path:
        gen = "false"
    elif "done" in request.path:
        gen = "done"
    else:
        gen = "open"

    params = Params()

    items = query_meta._items_menu(db, lang)
    countries = query_meta._countries(db)
    items = list(map(dict, items))

    if params.item:
        params.limit = None
        errors_groups = query._count(
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
            res["title"] = i10n_select_auto(res["title"], lang)
            res["menu"] = i10n_select_auto(res["menu"], lang)
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


@route("/issues/matrix.json")
def matrix(db, lang):
    params = Params(default_limit=None)
    errors_groups = query._count(
        db,
        params,
        ["markers.item", "markers.class", "sources.country", "items.menu->'en'"],
    )
    analysers = defaultdict(lambda: defaultdict(int))
    analysers_sum = defaultdict(int)
    countries_sum = defaultdict(int)
    total = 0
    for row in errors_groups:
        item, class_, country, menu, count = row
        analyser = "{}/{} {}".format(item, class_, menu)
        analysers[analyser][country] += count
        analysers_sum[analyser] += count
        countries_sum[country] += count
        total += count

    return dict(
        total=total,
        countries_sum=countries_sum,
        analysers_sum=analysers_sum,
        analysers=analysers,
    )
