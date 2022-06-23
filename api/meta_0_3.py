from bottle import default_app, request, response, route

from modules import query_meta
from modules.utils import LangsNegociation

app_0_2 = default_app.pop()


def _map_items(categories):
    for categorie in categories:
        categorie["categ"] = categorie["id"]
        del categorie["id"]
        for item in categorie["items"]:
            item["categ"] = item["categorie_id"]
            del item["categorie_id"]
    return categories


@route("/items")
def items(db, langs: LangsNegociation):
    return {"categories": _map_items(query_meta._items(db, langs=langs))}


@route("/items/<item:int>/class/<classs:int>")
def items_class(db, langs: LangsNegociation, item: int, classs: int):
    return {
        "categories": (query_meta._items(db, item=item, classs=classs, langs=langs))
    }


@route("/countries")
def countries(db):
    return {"countries": query_meta._countries(db)}


@route("/tags")
def tags(db):
    return {"tags": query_meta._tags(db)}


default_app.push(app_0_2)
