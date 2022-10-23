#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from typing import Dict, Set

from modules.dependencies import database

all_flags = [
    "O",
    "L",
    "K",
    "P",
    "M",
    "F",
    "=",
    "|",
    "||",
    "::",
    ".:.",
    "T",
    "t",
    "X",
    "><",
    "L'",
    "[]",
    ".",
    ".l",
    "'.",
    "/",
    "=-",
    "H",
    "h",
]


async def main():
    db = await database.get_dbconn()

    sql = """
CREATE TEMP TABLE marker_list_item AS
WITH RECURSIVE t AS (
   (SELECT item FROM markers ORDER BY item LIMIT 1)  -- parentheses required
   UNION ALL
   SELECT (SELECT item FROM markers WHERE item > t.item ORDER BY item LIMIT 1)
   FROM t
   WHERE t.item IS NOT NULL
   )
SELECT item FROM t WHERE item IS NOT NULL
"""
    await db.execute(sql)

    sql = """
SELECT
    m.item
FROM
    marker_list_item AS m
    LEFT JOIN items ON
        items.item = m.item
WHERE
    items.item IS NULL
ORDER BY
    m.item
"""

    prev_cat = -1
    colors: Dict[int, Set[str]] = {}
    items = {}

    for res in await db.fetch(sql):
        #  print res
        item = int(res[0])
        categ = int(item / 1000) * 10
        if categ == 80:
            fullcateg = categ + (item % 10)
        else:
            fullcateg = categ

        if prev_cat != categ:
            prev_cat = categ
            avail_flags = {}
            sql = "SELECT item, marker_color, marker_flag FROM items WHERE categorie_id = $1 ORDER BY item"
            for m in await db.fetch(sql, categ):
                items[m["item"]] = (m["marker_color"], m["marker_flag"])
                if categ == 80:
                    fullcateg_i = categ + (m["item"] % 10)
                else:
                    fullcateg_i = categ
                color = m["marker_color"]
                if fullcateg_i not in colors:
                    colors[fullcateg_i] = set()
                colors[fullcateg_i].add(color)
                if color not in avail_flags:
                    avail_flags[color] = all_flags[:]
                if m["marker_flag"] in avail_flags[color]:
                    avail_flags[color].remove(m["marker_flag"])

        chosen_color = None
        chosen_flag = None

        if categ == 80:
            item_group = (item // 10) * 10
            if (item_group + 0) in items:
                chosen_flag = items[item_group + 0][1]
            elif (item_group + 1) in items:
                chosen_flag = items[item_group + 1][1]
            elif (item_group + 2) in items:
                chosen_flag = items[item_group + 2][1]

        if chosen_flag:
            for c in colors[fullcateg]:
                if chosen_flag in avail_flags[c]:
                    chosen_color = c
                    continue

        else:
            for c in colors[fullcateg]:
                if len(avail_flags[c]) > 0:
                    chosen_color = c
                    chosen_flag = avail_flags[c][0]
                    continue

        if not chosen_color:
            print(f"Not enough available flags for item={item}")
            continue

        flag = chosen_flag.replace("'", "''")
        print(
            f"INSERT INTO items VALUES ({item}, {categ}, '{chosen_color}', '{flag}', NULL, ARRAY[1, 2, 3]);"
        )
        avail_flags[chosen_color].remove(chosen_flag)
        items[item] = (chosen_color, chosen_flag)


if __name__ == "__main__":
    asyncio.run(main())
