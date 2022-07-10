import re
from dataclasses import dataclass
from typing import List, Literal, Optional

from .. import utils

Status = Literal["open", "false"]
Fixable = Optional[Literal["online", "josm"]]


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


@dataclass
class Params:
    bbox: Optional[List[float]]
    item: Optional[str]
    source: Optional[int]
    classs: Optional[str]
    users: Optional[List[str]]
    level: Optional[List[int]]
    full: bool
    zoom: Optional[int]
    limit: int
    country: Optional[str]
    useDevItem: bool
    status: Optional[Status]
    start_date: Optional[str]
    end_date: Optional[str]
    tags: Optional[List[str]]
    fixable: Fixable
    osm_type: Optional[str]
    osm_id: Optional[int]
    tilex: Optional[int]
    tiley: Optional[int]

    def __init__(
        self,
        bbox: Optional[str],
        item: Optional[str],
        source: Optional[int],
        classs: Optional[str],
        username: Optional[str],
        level: Optional[str],
        full: bool,
        zoom: Optional[int],
        limit: int,
        country: Optional[str],
        useDev: bool,
        status: Optional[Status],
        start_date: Optional[str],
        end_date: Optional[str],
        tags: Optional[str],
        fixable: Fixable,
        osm_type: Optional[str],
        osm_id: Optional[int],
        tilex: Optional[int],
        tiley: Optional[int],
    ):
        bbox = bbox
        self.item = item
        self.source = source
        self.classs = classs
        users = username
        level = level
        self.full = full
        self.zoom = zoom
        self.limit = limit
        self.country = country
        self.useDevItem = useDev
        self.status = status
        self.start_date = start_date
        self.end_date = end_date
        tags = tags
        self.fixable = fixable
        self.osm_type = osm_type
        self.osm_id = osm_id
        self.tilex = tilex
        self.tiley = tiley

        if level:
            levels = level.split(",")
            try:
                self.level = [int(x) for x in levels if x]
            except Exception:
                self.level = [1, 2, 3]
        self.bbox = None
        if bbox:
            try:
                self.bbox = list(map(lambda x: float(x), bbox.split(",")))
            except Exception:
                pass
        self.users = users.split(",") if users else None
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


async def params(
    bbox: Optional[str] = None,
    item: Optional[str] = None,
    source: Optional[int] = None,
    classs: Optional[str] = None,
    users: Optional[str] = None,
    level: str = "1,2,3",
    full: bool = False,
    zoom: int = 10,
    limit: Optional[int] = 100,
    country: Optional[str] = None,
    useDevItem: bool = False,
    status: Optional[Status] = "open",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[str] = None,
    fixable: Fixable = None,
    osm_type: Optional[str] = None,
    osm_id: Optional[int] = None,
    tilex: Optional[int] = None,
    tiley: Optional[int] = None,
):
    return Params(
        bbox,
        item,
        source,
        classs,
        users,
        level,
        full,
        zoom,
        limit,
        country,
        useDevItem,
        status,
        start_date,
        end_date,
        tags,
        fixable,
        osm_type,
        osm_id,
        tilex,
        tiley,
    )