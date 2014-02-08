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

def _items(db, lang):
    sql = """
    SELECT
        item,
        menu
    FROM
        dynpoi_item
    ORDER BY
        item
    """
    db.execute(sql)
    return db.fetchall()


def _countries(db, lang):
    sql = """
    SELECT DISTINCT
        (string_to_array(comment,'-'))[array_upper(string_to_array(comment,'-'), 1)] AS country
    FROM
        dynpoi_source
    ORDER BY
        country
    """
    db.execute(sql)
    return db.fetchall()


def _categories(db, lang):
    sql = """
    SELECT
        dynpoi_categ.categ,
        dynpoi_categ.menu AS categ_menu,
        dynpoi_item.item,
        dynpoi_item.menu,
        dynpoi_item.marker_color,
        dynpoi_item.marker_flag,
        dynpoi_item.levels,
        dynpoi_item.number
    FROM
        dynpoi_categ
        JOIN dynpoi_item ON
            dynpoi_categ.categ = dynpoi_item.categ
    WHERE
        NOT dynpoi_item.levels = '{}'
    ORDER BY
        categ,
        item
    """
    result = []
    db.execute(sql)
    for res in db.fetchall():
        if result == [] or result[-1]["categ"] != res["categ"]:
            ret = {"categ":res["categ"], "menu": "no translation", "item": []}
            result.append(ret)
            for l in lang:
                if l in res["categ_menu"]:
                    ret["menu"] = res["categ_menu"][l]
                    break
        ret["item"].append({"item":res["item"], "menu":"no translation", "marker_color":res["marker_color"], "marker_flag":res["marker_flag"], "levels":res["levels"], "number":res["number"]})
        for l in lang:
            if res["menu"] and l in res["menu"]:
                ret["item"][-1]["menu"] = res["menu"][l]
                break

    return result


def _tags(db, lang):
    sql = """
    SELECT DISTINCT
        tag
    FROM
        (
        SELECT
            unnest(tags) AS tag
        FROM
            dynpoi_class
        ) AS t
    ORDER BY
        tag
    """
    db.execute(sql)
    return map(lambda x: x[0], db.fetchall())
