import re

from bottle import request

from . import utils


class Params:
    def __init__(self, default_limit=100, max_limit=500):
        self.bbox = request.query.getunicode("bbox", default=None)
        self.item = request.query.getunicode("item")
        self.source = request.query.getunicode("source", default="")
        self.classs = request.query.getunicode("class", default="")
        self.users = request.query.getunicode("username", default="")
        self.level = request.query.getunicode("level", default="1,2,3")
        self.full = request.query.getunicode("full", default=False)
        self.zoom = request.query.get("zoom", type=int, default=10)
        self.limit = request.query.get("limit", type=int, default=default_limit)
        self.country = request.query.getunicode("country", default=None)
        self.useDevItem = request.query.getunicode("useDevItem", default=False)
        self.status = request.query.getunicode("status", default="open")
        self.start_date = request.query.getunicode("start_date", default=None)
        self.end_date = request.query.getunicode("end_date", default=None)
        self.tags = request.query.getunicode("tags", default=None)
        self.fixable = request.query.getunicode("fixable", default=None)
        self.osm_type = request.query.getunicode("osm_type", default=None)
        self.osm_id = request.query.get("osm_id", type=int, default=None)
        self.tilex = request.query.getunicode("tilex", default=None)
        self.tiley = request.query.getunicode("tiley", default=None)

        if self.level:
            self.level = self.level.split(",")
            try:
                self.level = ",".join([str(int(x)) for x in self.level if x])
            except:
                self.level = "1,2,3"
        if self.bbox:
            try:
                self.bbox = list(map(lambda x: float(x), self.bbox.split(",")))
            except:
                self.bbox = None
        if self.users:
            self.users = self.users.split(",")
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
        if self.tags:
            self.tags = self.tags.split(",")

        if self.osm_type and self.osm_type not in ["node", "way", "relation"]:
            self.osm_type = None
        if self.osm_id and not self.osm_type:
            self.osm_id = None
