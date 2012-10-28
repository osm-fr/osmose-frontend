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

from bottle import route, request, template, response, redirect
from tools import utils
import datetime
import json


@route('/map')
def index_redirect():
    redirect("map/")

@route('/map/')
def index(db, lang):
    # valeurs par défaut
    lat    = request.params.get('lat', type=float, default=(request.get_cookie("lastLat") or "46.97"))
    lon    = request.params.get('lon', type=float, default=(request.get_cookie("lastLon") or "2.75"))
    zoom   = request.params.get('zoom', type=int, default=(request.get_cookie("lastZoom") or "6"))
    level  = request.params.get('level', default=(request.get_cookie("lastLevel") or "1"))
    source = request.params.get('source', default='')
    user   = request.params.get('user', default='')
    active_items = request.params.get('item', default=(request.get_cookie("lastItem") or None))

    if active_items:
        try:
            active_items = [int(x) for x in active_items if x]
        except:
            active_items = None

    if not active_items:
        active_items = []
        db.execute("SELECT item FROM dynpoi_item GROUP BY item;")
        for res in db.fetchall():
            active_items.append(int(res[0]))

    level_selected = {}
    for l in ("_all", "1", "2", "3", "1,2", "1,2,3"):
        level_selected[l] = ""

    if level == "":
        level_selected["1"] = " selected"
    elif level in ("1", "2", "3", "1,2", "1,2,3"):
        level_selected[level] = " selected"

    categories = utils.get_categories(lang)

    levels = {"1": set(), "2": set(), "3": set()}
    for categ in categories:
        for err in categ["item"]:
            for l in err["levels"]:
                levels[str(l)].add(err["item"])

    levels["1,2"] = levels["1"] | levels["2"]
    levels["1,2,3"] = levels["1,2"] | levels["3"]

    urls = []
    # TRANSLATORS: link to help in appropriate language
    urls.append((_("Help"), _("http://wiki.openstreetmap.org/wiki/Osmose")))
    urls.append((_("Errors by user"), "../byuser/"))
    urls.append((_("Relation analyser"), "http://analyser.openstreetmap.fr/"))
    # TRANSLATORS: this link can be changed to something specific to the language
    urls.append((_("CLC"), _("http://clc.openstreetmap.fr/")))
    # TRANSLATORS: this link can be changed to something specific to the language
    urls.append((_("Geodesic"), _("http://geodesie.openstreetmap.fr/")))
    # TRANSLATORS: this link can be changed to something specific to the language
    urls.append((_("openstreetmap.fr"), _("http://www.openstreetmap.fr/")))
    urls.append((_("Copyright"), "../copyright"))
    # TRANSLATORS: link to source code
    urls.append((_("Sources"), "https://gitorious.org/osmose"))
    urls.append((_("Statistics"), "../control/update"))

    allowed_languages = utils.allowed_languages

    return template('map/index', categories=categories, lat=lat, lon=lon, zoom=zoom, source=source, user=user,
        levels=levels, level_selected=level_selected, active_items=active_items, urls=urls, allowed_languages=allowed_languages, translate=utils.translator(lang))


@route('/map/markers')
def markers(db, lang):
    lat    = int(request.params.get('lat', type=float, default=0)*1000000)
    lon    = int(request.params.get('lon', type=float, default=0)*1000000)
    err_id = request.params.get('item', default='').split(',')
    err_id = ','.join([str(int(x)) for x in err_id if x])
    source = request.params.get('source', default='')
    user   = utils.pg_escape(unicode(request.params.get('user', default='')))
    level  = request.params.get('level', default='1')
    zoom   = request.params.get('zoom', type=int, default=10)
    bbox   = request.params.get('bbox')

    if level:
        level = level.split(",")
        level = ",".join([str(int(x)) for x in level if x])

    if bbox:
        bbox = bbox.split(",")
        try:
            minlon = int(1000000*float(bbox[0]))
            minlat = int(1000000*float(bbox[1]))
            maxlon = int(1000000*float(bbox[2]))
            maxlat = int(1000000*float(bbox[3]))
        except ValueError:
            minlon = lon - 100000
            minlat = lat - 100000
            maxlon = lon + 100000
            maxlat = lat + 100000

    expires = datetime.datetime.now() + datetime.timedelta(days=365)
    path = '/'.join(request.fullpath.split('/')[0:-1])
    response.set_cookie('lastLat', str(lat/1000000), expires=expires, path=path)
    response.set_cookie('lastLon', str(lon/1000000), expires=expires, path=path)
    response.set_cookie('lastZoom', str(zoom), expires=expires, path=path)
    response.set_cookie('lastLevel', str(level), expires=expires, path=path)
    response.set_cookie('lastItem', request.params.item, expires=expires, path=path)

    if (not user) and (not source) and (zoom < 6):
        return

    sqlbase  = """
    SELECT
        marker.id,
        marker.item,
        marker.lat,
        marker.lon
    FROM
        marker
        JOIN dynpoi_class ON
            marker.source = dynpoi_class.source AND
            marker.class = dynpoi_class.class
        JOIN dynpoi_update_last ON
            marker.source = dynpoi_update_last.source
        JOIN dynpoi_item ON
            marker.item = dynpoi_item.item
    WHERE
        %s AND
        (marker.lat BETWEEN %d AND %d) AND (marker.lon BETWEEN %d AND %d) AND
        dynpoi_update_last.timestamp > (now() - interval '3 months')
    ORDER BY
        point(marker.lat, marker.lon) <-> point(%d, %d)
    LIMIT 200
    """

    if source:
        sources = source.split(",")
        source2 = []
        for source in sources:
            source = source.split("-")
            if len(source)==1:
                source2.append("(marker.source=%d)"%int(source[0]))
            else:
                source2.append("(marker.source=%d AND marker.class=%d)"%(int(source[0]), int(source[1])))
        sources2 = " OR ".join(source2)
        where = "(%s)" % sources2
    elif err_id:
        where = "(marker.item IN (%s))" % err_id
    else:
        where = "1=1"

    if level:
        where += " AND dynpoi_class.level IN (%s)" % level

    if user:
        where += " AND ("
        s = []
        for f in xrange(3):
            s.append("elem%d.username = '%s'" % (f, user))
        where += " OR ".join(s)
        where += ")"

    db.execute(sqlbase % (where, minlat, maxlat, minlon, maxlon, lat, lon)) # FIXME pas de %
    results = db.fetchall()

    out = ["\t".join(["lat", "lon", "marker_id", "icon", "iconSize", "iconOffset", "html"])]
    for res in results:
        lat       = str(float(res["lat"])/1000000)
        lon       = str(float(res["lon"])/1000000)
        error_id  = res["id"]
        item      = res["item"] or 0
        marker = "../images/markers/marker-b-%d.png" % (res["item"])
        out.append("\t".join([lat, lon, str(error_id), marker, "17,33", "-8,-33", "plop"]).encode("utf8"))

    response.content_type = "text/plain; charset=utf-8"
    return "\n".join(out)


@route('/map/marker/<id:int>')
def markers(db, lang, id):
    data_type = { "N": "node", "W": "way", "R": "relation", "I": "infos"}

    # TRANSLATORS: link to tooltip help
    url_help = _("http://wiki.openstreetmap.org/wiki/Osmose/errors")
    sqlbase  = """
    SELECT marker.id,
       marker.item,
       marker.source,
       marker.class,
       marker.elems,
       marker.subclass,
       marker.lat,
       marker.lon,
       dynpoi_class.title,
       marker.subtitle,
       dynpoi_update_last.timestamp,
       elem0.data_type AS elem0_data_type,
       elem0.id AS elem0_id,
       elem0.tags AS elem0_tags,
       elem1.data_type AS elem1_data_type,
       elem1.id AS elem1_id,
       elem1.tags AS elem1_tags,
       elem2.data_type AS elem2_data_type,
       elem2.id AS elem2_id,
       elem2.tags AS elem2_tags,
    """

    for f in xrange(5):
        sqlbase += """
        fix%d.elem_data_type AS fix%d_elem_data_type,
        fix%d.elem_id AS fix%d_elem_id,
        fix%d.tags_create AS fix%d_tags_create,
        fix%d.tags_modify AS fix%d_tags_modify,
        fix%d.tags_delete AS fix%d_tags_delete,
        """ % (10 * (f, ))

    sqlbase += """0
    FROM
        marker
        JOIN dynpoi_class ON
            marker.source = dynpoi_class.source AND
            marker.class = dynpoi_class.class
        JOIN dynpoi_update_last ON
            marker.source = dynpoi_update_last.source
        JOIN dynpoi_item ON
            marker.item = dynpoi_item.item
    """

    for f in xrange(3):
        sqlbase += """
        LEFT JOIN marker_elem elem%d ON
            elem%d.marker_id = marker.id AND
            elem%d.elem_index = %d
    """ % (4 *(f, ))

    for f in xrange(5):
        sqlbase += """
        LEFT JOIN marker_fix fix%d ON
            fix%d.marker_id = marker.id AND
            fix%d.diff_index = %d
    """ % (4 * (f, ))

    sqlbase += """
    WHERE
        marker.id = %s
    """

    db.execute(sqlbase, (id,) )
    res = db.fetchone()

    translate = utils.translator(lang)

    lat       = str(float(res["lat"])/1000000)
    lon       = str(float(res["lon"])/1000000)
    error_id  = res["id"]
    title     = translate.select(res["title"])
    subtitle  = translate.select(res["subtitle"])
    b_date    = res["timestamp"] or ""
    item      = res["item"] or 0

    def expand_tags(tags, short = False):
      t = []
      if short:
        for k in tags:
          t.append({"k": k})
      else:
        for (k, v) in tags.items():
          t.append({"k": k, "v": v})
      return t

    elems = []
    for e in xrange(3):
      elem = "elem%d_" % e
      if res[elem + "data_type"]:
        tmp_elem = {data_type[res[elem + "data_type"]]: True,
                    "type": data_type[res[elem + "data_type"]],
                    "id": res[elem + "id"],
                    "tags": expand_tags(res[elem + "tags"]),
                    "fixes": [],
                   }
        for f in xrange(5):
          fix = "fix%d_" % f
          if (res[fix + "elem_data_type"] and
              res[fix + "elem_data_type"] == res[elem + "data_type"] and
              res[fix + "elem_id"] == res[elem + "id"]):
            tmp_elem["fixes"].append({"num": f,
                                      "add": expand_tags(res[fix + "tags_create"]),
                                      "mod": expand_tags(res[fix + "tags_modify"]),
                                      "del": expand_tags(res[fix + "tags_delete"], True),
                                     })
        elems.append(tmp_elem)


    new_elems = []
    for f in xrange(5):
        fix = "fix%d_" % f
        if res[fix + "elem_data_type"]:
            found = False
            for e in elems:
                if (e["type"] == data_type[res[fix + "elem_data_type"]] and
                    e["id"] == res[fix + "elem_id"]):

                    found = True
                    break
            if not found:
                new_elems.append({"num": f,
                                  "add": expand_tags(res[fix + "tags_create"]),
                                  "mod": expand_tags(res[fix + "tags_modify"]),
                                  "del": expand_tags(res[fix + "tags_delete"], True),
                                 })


    response.content_type = "application/json"
    return json.dumps({
        "website": utils.website,
        "lat":lat, "lon":lon,
        "minlat": float(lat) - 0.002, "maxlat": float(lat) + 0.002,
        "minlon": float(lon) - 0.002, "maxlon": float(lon) + 0.002,
        "error_id":error_id,
        "title":title, "subtitle":subtitle,
        "b_date":b_date.strftime("%Y-%m-%d"),
        "item":item,
        "elems":elems, "new_elems":new_elems,
        "elems_id":res["elems"].replace("_",","),
        "url_help":url_help
    })
