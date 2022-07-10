from collections import defaultdict
from typing import Optional

from asyncpg import Connection

from .utils import LangsNegociation, i10n_select


async def _items_menu(db: Connection, langs: LangsNegociation):
    sql = """
    SELECT
        item,
        menu
    FROM
        items
    ORDER BY
        item
    """
    return list(
        map(
            lambda x: {"item": x["item"], "menu": i10n_select(x["menu"], langs)},
            await db.fetch(sql),
        )
    )


async def _countries(db: Connection):
    sql = """
    SELECT DISTINCT
        country
    FROM
        sources
    ORDER BY
        country
    """
    return list(map(lambda x: x[0], await db.fetch(sql)))


async def _items(
    db: Connection,
    item: Optional[int] = None,
    classs: Optional[int] = None,
    langs: Optional[LangsNegociation] = None,
):
    sql_params = [item] if item is not None else []

    sql = (
        """
    SELECT
        id,
        menu AS title
    FROM
        categories
    WHERE
        1 = 1 """
        + (
            """AND id = CASE
            WHEN $1 < 1000 THEN 10
            ELSE ($1 / 1000)::int * 10
         END"""
            if item is not None
            else ""
        )
        + """
    ORDER BY
        id
    """
    )
    categs = await db.fetch(sql, *sql_params)

    sql = (
        """
    SELECT
        item,
        categorie_id,
        marker_color AS color,
        marker_flag AS flag,
        menu AS title,
        levels,
        number,
        tags
    FROM
        items
    WHERE
        1 = 1"""
        + ("AND item = $1" if item is not None else "")
        + """
    ORDER BY
        item
    """
    )
    items = await db.fetch(sql, *sql_params)
    items = list(
        map(
            lambda r: dict(
                r,
                title=i10n_select(r["title"], langs),
                levels=r["number"]
                and list(
                    map(
                        lambda l_n: {"level": l_n[0], "count": l_n[1]},
                        zip(r["levels"], r["number"]),
                    )
                )
                or list(map(lambda i: {"level": i, "count": 0}, [1, 2, 3])),
            ),
            items,
        )
    )
    items_categ = defaultdict(list)
    for i in items:
        items_categ[i["categorie_id"]].append(i)

    sql = """
    SELECT
        item,
        class,
        title,
        level,
        tags,
        detail,
        fix,
        trap,
        example,
        source,
        resource
    FROM
        class
    WHERE
        1 = 1"""
    params = 0
    if item is not None:
        params += 1
        sql += f"AND item = ${params}"
    if classs is not None:
        params += 1
        sql += f"AND class = ${params}"
        sql_params.append(classs)
    sql += """
    ORDER BY
        item,
        class
    """
    classs = await db.fetch(sql, *sql_params)
    classs = list(
        map(
            lambda c: dict(
                dict(c),
                title=i10n_select(c["title"], langs),
                detail=i10n_select(c["detail"], langs),
                fix=i10n_select(c["fix"], langs),
                trap=i10n_select(c["trap"], langs),
                example=i10n_select(c["example"], langs),
            ),
            classs,
        )
    )
    class_item = defaultdict(list)
    for c in classs:
        class_item[c["item"]].append(c)

    return list(
        map(
            lambda categ: dict(
                categ,
                items=list(
                    map(
                        lambda item: dict(item, **{"class": class_item[item["item"]]}),
                        items_categ[categ["id"]],
                    )
                ),
            ),
            map(
                lambda categ: {
                    "id": categ["id"],
                    "title": i10n_select(categ["title"], langs),
                },
                categs,
            ),
        )
    )


async def _tags(db: Connection):
    sql = """
    SELECT DISTINCT
        tag
    FROM
        (
        SELECT
            unnest(tags) AS tag
        FROM
            class
        ) AS t
    WHERE
        tag != ''
    ORDER BY
        tag
    """
    return list(map(lambda x: x[0], await db.fetch(sql)))
