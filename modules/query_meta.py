#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

from collections import defaultdict
from .utils import i10n_select


def _items(db, lang):
    sql = """
    SELECT
        item,
        menu
    FROM
        items
    ORDER BY
        item
    """
    db.execute(sql)
    return db.fetchall()


def _countries(db, lang):
    sql = """
    SELECT DISTINCT
        country
    FROM
        sources
    ORDER BY
        country
    """
    db.execute(sql)
    return db.fetchall()

def _countries_3(db):
    sql = """
    SELECT DISTINCT
        country
    FROM
        sources
    ORDER BY
        country
    """
    db.execute(sql)
    return list(map(lambda x: x[0], db.fetchall()))


def _categories(db, lang):
    sql = """
    SELECT
        items.categorie_id,
        categories.menu AS categ_menu,
        items.item,
        items.menu,
        items.marker_color,
        items.marker_flag,
        items.levels,
        items.number,
        items.tags
    FROM
        categories
        JOIN items ON
            categories.id = items.categorie_id
    ORDER BY
        categorie_id,
        item
    """
    result = []
    db.execute(sql)
    for res in db.fetchall():
        if result == [] or result[-1]["categorie_id"] != res["categorie_id"]:
            ret = {"categorie_id":res["categorie_id"], "menu": "no translation", "item": []}
            result.append(ret)
            ret["menu_lang"] = {k: v for k, v in res["categ_menu"].items() if v}
            for l in lang:
                if l in res["categ_menu"]:
                    ret["menu"] = res["categ_menu"][l]
                    break
        ret["item"].append({"item":res["item"], "menu":"no translation", "marker_color":res["marker_color"], "marker_flag":res["marker_flag"], "levels":res["levels"], "number":res["number"], "tags":res["tags"]})
        for l in lang:
            if res["menu"] and l in res["menu"]:
                ret["item"][-1]["menu"] = res["menu"][l]
                break

    return result


def _items_3(db, item = None, classs = None, langs = None):
    sql = """
    SELECT
        id,
        menu AS title
    FROM
        categories
    WHERE
        1 = 1 """ + \
        ("""AND id = CASE
            WHEN %(item)s < 1000 THEN 10
            ELSE (%(item)s / 1000)::int * 10
         END""" if item != None else '') + \
    """
    ORDER BY
        id
    """
    db.execute(sql, {'item': item})
    categs = db.fetchall()
    for categ in categs:
        categ['title'] = i10n_select(categ['title'], langs)

    sql = """
    SELECT
        item,
        categorie_id,
        marker_color AS color,
        menu AS title,
        levels,
        number,
        tags
    FROM
        items
    WHERE
        1 = 1""" + \
        ("AND item = %(item)s" if item != None else '') + \
    """
    ORDER BY
        item
    """
    db.execute(sql, {'item': item})
    items = db.fetchall()
    items = list(map(lambda r: dict(
        r,
        title = i10n_select(r['title'], langs),
        levels = r['number'] and list(map(lambda l_n: {'level': l_n[0], 'count': l_n[1]}, zip(r['levels'], r['number']))) or list(map(lambda i: {'level': i, 'count': 0}, [1, 2, 3])),
    ), items))
    items_categ = defaultdict(list)
    for i in items:
        items_categ[i['categorie_id']].append(i)

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
        1 = 1""" + \
        ("AND item = %(item)s" if item != None else '') + \
        ("AND class = %(classs)s" if classs != None else '') + \
    """
    ORDER BY
        item,
        class
    """
    db.execute(sql, {'item': item, 'classs': classs})
    classs = db.fetchall()
    classs = list(map(lambda c: dict(
        dict(c),
        title = i10n_select(c['title'], langs),
        detail = i10n_select(c['detail'], langs),
        fix = i10n_select(c['fix'], langs),
        trap = i10n_select(c['trap'], langs),
        example = i10n_select(c['example'], langs),
    ), classs))
    class_item = defaultdict(list)
    for c in classs:
        class_item[c['item']].append(c)

    return list(map(lambda categ:
        dict(
            categ,
            items = list(map(lambda item:
                dict(
                    item,
                    **{'class': class_item[item['item']]}
                ),
                items_categ[categ['id']]))
        ),
        categs))


def _tags(db):
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
    db.execute(sql)
    return list(map(lambda x: x[0], db.fetchall()))
