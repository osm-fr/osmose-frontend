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

from bottle import route, request, template, response, abort, redirect
from tools import utils
import StringIO, re

import errors_graph


def int_list(s):
    return map(lambda x: int(x), filter(lambda x: x and x!='',s).split(','))

@route('/errors/graph.png')
def graph(db):
    class options:
        sources = request.params.get('sources', type=int_list, default=[])
        classes = request.params.get('class', type=int_list, default=[])
        items   = request.params.get('item', type=int_list, default=[])
        country = request.params.get('country')
        if country <> None and not re.match(r"^([a-z_]+)$", country):
            country = None

    try:
        data = errors_graph.make_plt(db, options)
        response.content_type = "image/png"
        return data
    except Exception, e:
        response.content_type = "text/plain"
        import traceback
        out = StringIO.StringIO()
        traceback.print_exc(file=out)
        return out.getvalue() + "\n"


@route('/errors')
def index_redirect():
    redirect("errors/")


@route('/errors/')
@route('/errors/done')
@route('/errors/false-positive')
def index(db, lang):
    source  = request.params.get('source', type=int)
    class_  = request.params.get('class', type=int)
    item    = request.params.get('item', type=int)
    country = request.params.get('country')
    num_points = request.params.get('points', type=int)
    show_all = request.params.get('all')

    if country and not re.match(r"^([a-z_]+)$", country):
        country = None

    if num_points <= 0:
        num_points = None
    elif num_points > 10000:
        num_points = 10000

    if request.path.endswith("false-positive"):
        title = _("False positives")
        gen = "false-positive"
        default_show_all = False
    elif request.path.endswith("done"):
        title = _("Fixed errors")
        gen = "done"
        default_show_all = False
    else:
        title = _("Informations")
        gen = "info"
        default_show_all = True

    if show_all == None:
        show_all = default_show_all
    elif int(show_all) == 0:
        show_all = False
    else:
        show_all = True

    sql = """
    SELECT DISTINCT
        (string_to_array(comment,'-'))[array_upper(string_to_array(comment,'-'), 1)] AS country
    FROM
        dynpoi_source
    ORDER BY
        country
    """
    db.execute(sql)
    countries = db.fetchall()

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
    items = db.fetchall()

    sql = """
    SELECT
        dynpoi_class.source AS source,
        dynpoi_class.class AS class,
        dynpoi_class.item AS item,
        first(dynpoi_item.menu) AS menu,
        first(dynpoi_class.title) AS title,
        %s AS count,
        dynpoi_source.comment AS source_comment
    FROM
        dynpoi_class
        LEFT JOIN dynpoi_item ON 
            dynpoi_class.item = dynpoi_item.item
        LEFT JOIN dynpoi_source ON
            dynpoi_class.source = dynpoi_source.source
        %s %s
    WHERE 1=1
        %s
    GROUP BY
        dynpoi_class.source,
        dynpoi_class.class,
        dynpoi_class.item,
        dynpoi_source.comment
    ORDER BY
        dynpoi_class.item,
        dynpoi_class.source
    """

    if show_all:
        opt_left_join = "LEFT"
    else:
        opt_left_join = ""

    if gen == "info":
        opt_count = "count(marker.source)"
        opt_join = """
        JOIN marker ON
            dynpoi_class.source = marker.source AND
            dynpoi_class.class = marker.class
        """
    elif gen == "false-positive":
        opt_count = "count(dynpoi_status.source)"
        opt_join = """
        JOIN dynpoi_status ON
            dynpoi_class.source = dynpoi_status.source AND
            dynpoi_class.class = dynpoi_status.class AND
            dynpoi_status.status = 'false'
        """
    elif gen == "done":
        opt_count = "count(dynpoi_status.source)"
        opt_join = """
        JOIN dynpoi_status ON
            dynpoi_class.source = dynpoi_status.source AND
            dynpoi_class.class = dynpoi_status.class AND
            dynpoi_status.status = 'done'
        """

    opt_where = ""

    if source <> None:
        opt_where += " AND dynpoi_class.source = %s" % source
    if class_ <> None:
        opt_where += " AND dynpoi_class.class = %s" % class_
    if item <> None:
        opt_where += " AND dynpoi_class.item = %s" % item
    if country <> None:
        opt_where += " AND dynpoi_source.comment LIKE '%%%s'" % ("-" + country)

    if source == None and item == None and country == None:
        if show_all:
            opt_count = "-1"
            if gen == "info":
                opt_left_join = ""
                opt_join = ""

    sql = sql % (opt_count, opt_left_join, opt_join, opt_where)

    db.execute(sql)
    errors_groups = db.fetchall()
    total = 0
    for res in errors_groups:
        if res["count"] != -1:
            total += res["count"]

    if (total > 0 and total < 1000) or num_points:
        if gen == "info":
            opt_count = "count(marker.source)"
            opt_join = """
            JOIN marker ON
                dynpoi_class.source = marker.source AND
                dynpoi_class.class = marker.class
            """

        sql = """
        SELECT
            %s
            dynpoi_class.source AS source,
            dynpoi_class.class AS class,
            dynpoi_class.item AS item,
            dynpoi_class.level AS level,
            dynpoi_item.menu,
            dynpoi_class.title,
            subtitle,
            dynpoi_source.comment AS source_comment,
            subclass,
            lat,
            lon,
            elems AS elems,
            %s AS date
        FROM
            dynpoi_class
            LEFT JOIN dynpoi_item ON
                dynpoi_class.item = dynpoi_item.item
            LEFT JOIN dynpoi_source ON
                dynpoi_class.source = dynpoi_source.source
            %s
        WHERE 1=1
            %s
        ORDER BY
            %s
            dynpoi_class.item,
            dynpoi_class.source
        """

        if gen == "info":
            marker_id = "marker.id AS marker_id,"
            opt_date = "-1"
            opt_order = "subtitle->'en',"
        elif gen in ("false-positive", "done"):
            marker_id = ""
            opt_date = "date"
            opt_order = "dynpoi_status.date DESC,"
        if num_points:
            sql += "LIMIT %d" % num_points

        sql = sql % ((marker_id, ) + (opt_date, opt_join, opt_where, opt_order))
        db.execute(sql)
        errors = db.fetchall()
    else:
        opt_date = None
        errors = None

    return template('errors/index', countries=countries, items=items, errors_groups=errors_groups, total=total, errors=errors, query=request.query_string, country=country, item=item, translate=utils.translator(lang), gen=gen, opt_date=opt_date, title=title)
