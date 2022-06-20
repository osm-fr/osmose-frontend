import re
from typing import List, Union

from bottle import request

from . import utils


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

    def __init__(self, default_limit=100, max_limit=500):
        bbox = request.query.getunicode("bbox", default=None)
        self.item = request.query.getunicode("item")
        self.source = request.query.getunicode("source", default="")
        self.classs = request.query.getunicode("class", default="")
        users = request.query.getunicode("username", default="")
        self.level = request.query.getunicode("level", default="1,2,3")
        self.full = request.query.getunicode("full", default=False)
        self.zoom = request.query.get("zoom", type=int, default=10)
        self.limit = request.query.get("limit", type=int, default=default_limit)
        self.country = request.query.getunicode("country", default=None)
        self.useDevItem = request.query.getunicode("useDevItem", default=False)
        self.status = request.query.getunicode("status", default="open")
        self.start_date = request.query.getunicode("start_date", default=None)
        self.end_date = request.query.getunicode("end_date", default=None)
        tags = request.query.getunicode("tags", default=None)
        self.fixable = request.query.getunicode("fixable", default=None)
        self.osm_type = request.query.getunicode("osm_type", default=None)
        self.osm_id = request.query.get("osm_id", type=int, default=None)
        self.tilex = request.query.getunicode("tilex", default=None)
        self.tiley = request.query.getunicode("tiley", default=None)

        if self.level:
            levels = self.level.split(",")
            try:
                self.level = ",".join([str(int(x)) for x in levels if x])
            except:
                self.level = "1,2,3"
        if bbox:
            try:
                self.bbox = list(map(lambda x: float(x), bbox.split(",")))
            except:
                self.bbox = None
        if users:
            self.users = users.split(",")
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
        if tags:
            self.tags = tags.split(",")

        if self.osm_type and self.osm_type not in ["node", "way", "relation"]:
            self.osm_type = None
        if self.osm_id and not self.osm_type:
            self.osm_id = None
