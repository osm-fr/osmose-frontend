import re
from dataclasses import dataclass
from typing import List, Literal, Union

from .. import utils

Status = Literal["open", "false"]
Fixable = Union[None, Literal["online", "josm"]]


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


@dataclass
class Params:
    bbox: Union[List[float], None]
    item: Union[str, None]
    source: Union[int, None]
    classs: Union[str, None]
    users: Union[List[str], None]
    level: Union[List[int], None]
    full: bool
    zoom: Union[int, None]
    limit: int
    country: Union[str, None]
    useDevItem: bool
    status: Union[Status, None]
    start_date: Union[str, None]
    end_date: Union[str, None]
    tags: Union[List[str], None]
    fixable: Fixable
    osm_type: Union[str, None]
    osm_id: Union[int, None]
    tilex: Union[int, None]
    tiley: Union[int, None]

    def __init__(
        self,
        bbox: Union[str, None],
        item: Union[str, None],
        source: Union[int, None],
        classs: Union[str, None],
        username: Union[str, None],
        level: Union[str, None],
        full: bool,
        zoom: Union[int, None],
        limit: int,
        country: Union[str, None],
        useDev: bool,
        status: Union[Status, None],
        start_date: Union[str, None],
        end_date: Union[str, None],
        tags: Union[str, None],
        fixable: Fixable,
        osm_type: Union[str, None],
        osm_id: Union[int, None],
        tilex: Union[int, None],
        tiley: Union[int, None],
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
    bbox: Union[str, None] = None,
    item: Union[str, None] = None,
    source: Union[int, None] = None,
    classs: Union[str, None] = None,
    users: Union[str, None] = None,
    level: str = "1,2,3",
    full: bool = False,
    zoom: int = 10,
    limit: Union[int, None] = 100,
    country: Union[str, None] = None,
    useDevItem: bool = False,
    status: Union[Status, None] = "open",
    start_date: Union[str, None] = None,
    end_date: Union[str, None] = None,
    tags: Union[str, None] = None,
    fixable: Fixable = None,
    osm_type: Union[str, None] = None,
    osm_id: Union[int, None] = None,
    tilex: Union[int, None] = None,
    tiley: Union[int, None] = None,
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
