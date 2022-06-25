import re
from typing import List, Union

from fastapi import Request

from . import utils


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


class Params:
    bbox: Union[List[float], None]
    item: Union[str, None]
    source: Union[int, None]
    classs: Union[str, None]
    users: Union[List[str], None]
    level: Union[str, None]
    full: bool
    zoom: Union[int, None]
    limit: int
    country: Union[str, None]
    useDevItem: bool
    status: Union[str, None]
    start_date: Union[str, None]
    end_date: Union[str, None]
    tags: Union[List[str], None]
    fixable: Union[bool, None]
    osm_type: Union[str, None]
    osm_id: Union[int, None]
    tilex: Union[int, None]
    tiley: Union[int, None]

    def __init__(self, request: Request, default_limit=100, max_limit=500):
        bbox = request.query_params.get("bbox", None)
        self.item = request.query_params.get("item")
        self.source = request.query_params.get("source", "")
        self.classs = request.query_params.get("class", "")
        users = request.query_params.get("username", "")
        self.level = request.query_params.get("level", "1,2,3")
        self.full = request.query_params.get("full", False)
        self.zoom = safe_cast(request.query_params.get("zoom"), int, 10)
        self.limit = safe_cast(request.query_params.get("limit"), int, default_limit)
        self.country = request.query_params.get("country", None)
        self.useDevItem = request.query_params.get("useDevItem", False)
        self.status = request.query_params.get("status", "open")
        self.start_date = request.query_params.get("start_date", None)
        self.end_date = request.query_params.get("end_date", None)
        tags = request.query_params.get("tags", None)
        self.fixable = request.query_params.get("fixable", None)
        self.osm_type = request.query_params.get("osm_type", None)
        self.osm_id = safe_cast(request.query_params.get("osm_id"), int, None)
        self.tilex = request.query_params.get("tilex", None)
        self.tiley = request.query_params.get("tiley", None)

        if self.level:
            levels = self.level.split(",")
            try:
                self.level = ",".join([str(int(x)) for x in levels if x])
            except Exception:
                self.level = "1,2,3"
        self.bbox = None
        if bbox:
            try:
                self.bbox = list(map(lambda x: float(x), bbox.split(",")))
            except Exception:
                pass
        self.users = users.split(",") if users else None
        if self.limit is not None and self.limit > max_limit:
            self.limit = max_limit
        if self.country and not re.match(r"^([a-z_]+)(\*|)$", self.country):
            self.country = ""
        if self.useDevItem == "true":
            self.useDevItem = True
        elif self.useDevItem == "all":
            pass
        else:
            self.useDevItem = False
        if self.start_date:
            self.start_date = utils.str_to_datetime(self.start_date)
        if self.end_date:
            self.end_date = utils.str_to_datetime(self.end_date)
        self.tags = tags.split(",") if tags else None

        if self.osm_type and self.osm_type not in ["node", "way", "relation"]:
            self.osm_type = None
        if self.osm_id and not self.osm_type:
            self.osm_id = None
