import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Literal, Optional, Union

from fastapi import Query
from fastapi.params import Query as QueryObject

from .. import utils

Status = Literal["open", "false", "done"]
Fixable = Optional[Literal["online", "josm"]]
UseDevItem = Literal["false", "true", "all"]


@dataclass
class Params:
    bbox: Optional[List[float]] = None
    item: Optional[str] = None
    source: List[List[int]] = field(default_factory=list)
    classs: List[int] = field(default_factory=list)
    users: Optional[List[str]] = None
    level: Optional[List[int]] = None
    full: bool = False
    zoom: Optional[int] = None
    limit: int = 100
    country: Optional[str] = None
    useDevItem: UseDevItem = "false"
    status: Optional[Status] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    tags: Optional[List[str]] = None
    fixable: Fixable = None
    osm_type: Optional[str] = None
    osm_id: Optional[int] = None
    tilex: Optional[int] = None
    tiley: Optional[int] = None

    def __init__(
        self,
        bbox: Optional[str],
        item: Optional[str],
        source: Optional[str],
        classs: Optional[str],
        users: Optional[str],
        level: Optional[str],
        full: bool,
        zoom: Optional[int],
        limit: int,
        country: Optional[str],
        useDevItem: Optional[str],
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
        source = source
        classs = classs
        users = users
        level = level
        self.full = full
        self.zoom = zoom
        self.limit = limit
        self.country = country
        useDevItem = useDevItem
        self.status = status
        start_date = start_date
        end_date = end_date
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
        if bbox:
            try:
                self.bbox = list(map(lambda x: float(x), bbox.split(",")))
            except Exception:
                pass
        self.source = []
        if source:
            sources = source.split(",")
            try:
                self.source = list(
                    map(lambda source: list(map(int, source.split("-"))), sources)
                )
            except Exception:
                pass
        self.classs = []
        if classs:
            sources = classs.split(",")
            try:
                self.classs = list(map(lambda x: int(x), classs.split(",")))
            except Exception:
                pass
        self.users = users.split(",") if users else None
        if self.country and not re.match(r"^([a-z_]+)(\*|)$", self.country):
            self.country = ""
        if useDevItem == "true":
            self.useDevItem = "true"
        elif useDevItem == "all":
            self.useDevItem = "all"
        else:
            self.useDevItem = "false"
        if start_date:
            self.start_date = utils.str_to_datetime(start_date)
        if end_date:
            self.end_date = utils.str_to_datetime(end_date)
        self.tags = tags.split(",") if tags else None

        if self.osm_type and self.osm_type not in ["node", "way", "relation"]:
            self.osm_type = None
        if self.osm_id and not self.osm_type:
            self.osm_id = None


async def params(
    bbox: Optional[str] = None,
    item: Optional[str] = None,
    source: Optional[str] = None,
    classs: Optional[str] = Query(default=None, alias="class"),
    username: Optional[str] = None,
    level: str = "1,2,3",
    full: bool = False,
    zoom: int = 10,
    limit: Optional[Union[int, Literal[""]]] = 100,
    country: Optional[str] = None,
    useDevItem: Optional[str] = None,
    status: Optional[Status] = "open",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    tags: Optional[str] = None,
    fixable: Union[Fixable, Literal[""]] = "",
    osm_type: Optional[str] = None,
    osm_id: Optional[int] = None,
    tilex: Optional[int] = None,
    tiley: Optional[int] = None,
) -> Params:
    # Workaround on Query default value, we should not get a Query object here
    if isinstance(classs, QueryObject):
        classs = classs.default

    return Params(
        bbox,
        item,
        source,
        classs,
        username if username != "" else None,
        level,
        full,
        zoom,
        limit if limit != "" and limit is not None else 100,
        country if country != "" else None,
        useDevItem,
        status if status != "" else None,
        start_date if start_date != "" else None,
        end_date if end_date != "" else None,
        tags if tags != "" else None,
        fixable if fixable != "" else None,
        osm_type,
        osm_id,
        tilex,
        tiley,
    )
