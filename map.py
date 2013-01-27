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

from bottle import route, request, template, response, redirect, abort
from tools import utils
from tools import tag2link
import datetime
import json
import math, StringIO
from PIL import Image
import ImageDraw

t2l = tag2link.tag2link("tools/tag2link_sources.xml")

def check_items(items, all_items):
    if items == None or items == 'xxxx':
        return all_items
    else:
        items = items.split(',')
        return filter(lambda i: str(i) in items or str(i)[0]+'xxx' in items, all_items)


@route('/map')
def index_redirect():
    new_url = "map/"
    if request.query_string:
        new_url += "?"
        new_url += request.query_string
    redirect(new_url)

@route('/map/')
def index(db, lang):
    # valeurs par défaut
    params = { "lat":    46.97,
               "lon":    2.75,
               "zoom":   6,
               "item":   None,
               "level":  1,
               "source": '',
               "class":  '',
               "user":   '',
             }

    for p in ["lat", "lon", "zoom", "item", "level"]:
        if request.cookies.get("last_" + p, default=None):
            params[p] = request.cookies.get("last_" + p)

    for p in ["lat", "lon", "zoom", "item", "level", "source", "user", "class"]:
        if request.params.get(p, default=None):
            params[p] = request.params.get(p)

    for p in ["lat", "lon"]:
        params[p] = float(params[p])

    for p in ["zoom"]:
        params[p] = int(params[p])

    all_items = []
    db.execute("SELECT item FROM dynpoi_item GROUP BY item;")
    for res in db.fetchall():
        all_items.append(int(res[0]))
    active_items = check_items(params["item"], all_items)

    level_selected = {}
    for l in ("_all", "1", "2", "3", "1,2", "1,2,3"):
        level_selected[l] = ""

    if params["level"] == "":
        level_selected["1"] = " selected=\"selected\""
    elif params["level"] in ("1", "2", "3", "1,2", "1,2,3"):
        level_selected[params["level"]] = " selected=\"selected\""

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
    urls.append((_("Errors by user"), "../byuser/"))
    urls.append((_("Relation analyser"), "http://analyser.openstreetmap.fr/"))
    # TRANSLATORS: this link can be changed to something specific to the language
    urls.append((_("CLC"), _("http://clc.openstreetmap.fr/")))
    # TRANSLATORS: this link can be changed to something specific to the language
    urls.append((_("openstreetmap.fr"), _("http://www.openstreetmap.fr/")))
    # TRANSLATORS: link to source code
    urls.append((_("Statistics"), "../control/update"))

    helps = []
    helps.append((_("Help on wiki"), _("http://wiki.openstreetmap.org/wiki/Osmose")))
    helps.append((_("Copyright"), "../copyright"))
    helps.append((_("Sources"), "https://gitorious.org/osmose"))
    helps.append((_("Translation"), "../translation"))

    allowed_languages = utils.allowed_languages

    sql = """
SELECT
    EXTRACT(EPOCH FROM ((now())-timestamp)) AS age
FROM
    dynpoi_update_last
ORDER BY
    timestamp
LIMIT
    1
OFFSET
    (SELECT COUNT(*)/2 FROM dynpoi_update_last)
;
"""
    db.execute(sql)
    delay = db.fetchone()
    if delay:
        delay = delay[0]/60/60/24

    return template('map/index', categories=categories, lat=params["lat"], lon=params["lon"], zoom=params["zoom"],
        source=params["source"], user=params["user"], classs=params["class"],
        levels=levels, level_selected=level_selected, active_items=active_items, urls=urls, helps=helps, delay=delay,
        allowed_languages=allowed_languages, translate=utils.translator(lang),
        website=utils.website, request=request)


def build_where_item(item, table):
    if item == '':
        where = "1=2"
    elif item == None or item == 'xxxx':
        where = "1=1"
    else:
        where = []
        l = []
        for i in item.split(','):
            try:
                if 'xxx' in i:
                    where.append("%s.item/1000 = %s" % (table, int(i[0])))
                else:
                    l.append(str(int(i)))
            except:
                pass
        if l != []:
            where.append("%s.item IN (%s)" % (table, ','.join(l)))
        if where != []:
            where = "(%s)" % ' OR '.join(where)
        else:
            where = "1=1"
    return where


def build_param(source, item, level, user, classs):
    join = ""
    where = []
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
        where.append("(%s)" % sources2)

    if item:
        where.append(build_where_item(item, "marker"))

    if level and level != "(1,2,3)":
        join += """
        JOIN dynpoi_class ON
            marker.source = dynpoi_class.source AND
            marker.class = dynpoi_class.class
        """
        where.append("dynpoi_class.level IN (%s)" % level)

    if user:
        join += """
        JOIN marker_elem ON
            marker_elem.marker_id = marker.id
        """
        where.append("marker_elem.username = '%s'" % user)

    if classs:
        where.append("marker.class = %d"%int(classs))

    return (join, " AND ".join(where))


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)

@route('/map/heat/<z:int>/<x:int>/<y:int>.png')
def heat(db, z, x, y):
    x2,y1 = num2deg(x,y,z)
    x1,y2 = num2deg(x+1,y+1,z)

    item   = request.params.get('item')
    source = request.params.get('source', default='')
    classs = request.params.get('class', default='')
    user   = utils.pg_escape(unicode(request.params.get('user', default='')))
    level  = request.params.get('level', default='1')

    COUNT=32

    items = build_where_item(item, "dynpoi_item")

    db.execute("""
SELECT
    SUM((SELECT SUM(t) FROM UNNEST(number) t))
FROM
    dynpoi_item
WHERE
""" + items)
    max = db.fetchone()
    if max and max[0]:
        max = float(max[0])
    else:
        # FIXME redirect empty tile
        max = 0

    join, where = build_param(source, item, level, user, classs)

    db.execute("""
SELECT
    COUNT(*),
    (((lon-%(y1)s))*%(count)s/(%(y2)s-%(y1)s)-0.5)::int AS latn,
    (((lat-%(x1)s))*%(count)s/(%(x2)s-%(x1)s)-0.5)::int AS lonn
FROM
    marker
""" + join + """
WHERE
""" + where + """ AND
    lat>%(x1)s::int AND
    lon>%(y1)s::int AND
    lat<%(x2)s::int AND
    lon<%(y2)s::int
GROUP BY
    latn,
    lonn
""", {"x1":x1*10e5, "y1":y1*10e5, "x2":x2*10e5, "y2":y2*10e5, "count":COUNT})
    im = Image.new("RGB", (256,256), "#ff0000")
    draw = ImageDraw.Draw(im)

    transparent_area = (0,0,256,256)
    mask = Image.new('L', im.size, color=255)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rectangle(transparent_area, fill=0)

    for row in db.fetchall():
        count, x, y = row
        count = int(math.log(count) / math.log(max / ((z-4+1+math.sqrt(COUNT))**2)) * 255)
        count = 255 if count > 255 else count
        r = [(x*256/COUNT,(COUNT-1-y)*256/COUNT), ((x+1)*256/COUNT-1,((COUNT-1-y+1)*256/COUNT-1))]
        mask_draw.rectangle(r, fill=count)

    im.putalpha(mask)
    del draw

    buf = StringIO.StringIO()
    im.save(buf, 'PNG')
    response.content_type = 'image/png'
    return buf.getvalue()


@route('/map/markers')
def markers(db, lang):
    lat    = int(request.params.get('lat', type=float, default=0)*1000000)
    lon    = int(request.params.get('lon', type=float, default=0)*1000000)
    item   = request.params.get('item')
    source = request.params.get('source', default='')
    classs = request.params.get('class', default='')
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
    response.set_cookie('last_lat', str(lat/1000000.), expires=expires, path=path)
    response.set_cookie('last_lon', str(lon/1000000.), expires=expires, path=path)
    response.set_cookie('last_zoom', str(zoom), expires=expires, path=path)
    response.set_cookie('last_level', str(level), expires=expires, path=path)
    response.set_cookie('last_item', request.params.item, expires=expires, path=path)

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
        JOIN dynpoi_update_last ON
            marker.source = dynpoi_update_last.source
        JOIN dynpoi_item ON
            marker.item = dynpoi_item.item
        %s
    WHERE
        %s AND
        dynpoi_update_last.timestamp > (now() - interval '3 months')
    ORDER BY
        point(marker.lat, marker.lon) <-> point(%d, %d)
    LIMIT 200
    """

    join, where = build_param(source, item, level, user, classs)
    db.execute(sqlbase % (join, where, lat, lon)) # FIXME pas de %
    results = db.fetchall()

    out = ["\t".join(["lat", "lon", "marker_id", "item"])]
    for res in results:
        lat       = str(float(res["lat"])/1000000)
        lon       = str(float(res["lon"])/1000000)
        error_id  = res["id"]
        item      = res["item"] or 0
        out.append("\t".join([lat, lon, str(error_id), str(item)]))

    response.content_type = "text/plain; charset=utf-8"
    return "\n".join(out)

@route('/tpl/popup.tpl')
def popup_template(lang):

    return template('map/popup', mustache_delimiter="{{=<% %>=}}",
                                 website=utils.website)


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

    if not res:
        abort(410, "Id is not present in database.")

    translate = utils.translator(lang)

    lat       = str(float(res["lat"])/1000000)
    lon       = str(float(res["lon"])/1000000)
    error_id  = res["id"]
    title     = translate.select(res["title"])
    subtitle  = translate.select(res["subtitle"])
    b_date    = res["timestamp"] or ""
    item      = res["item"] or 0

    def expand_tags(tags, links, short = False):
      t = []
      if short:
        for k in tags:
          t.append({"k": k})
      else:
        for (k, v) in tags.items():
          if links and links.has_key(k):
            t.append({"k": k, "v": v, "vlink": links[k]})
          else:
            t.append({"k": k, "v": v})
      return t

    elems = []
    for e in xrange(3):
      elem = "elem%d_" % e
      if res[elem + "data_type"]:
        tags = res[elem + "tags"]
        try:
            links = t2l.checkTags(tags)
        except:
            links = {}
        tmp_elem = {data_type[res[elem + "data_type"]]: True,
                    "type": data_type[res[elem + "data_type"]],
                    "id": res[elem + "id"],
                    "tags": expand_tags(tags, links),
                    "fixes": [],
                   }
        for f in xrange(5):
          fix = "fix%d_" % f
          if (res[fix + "elem_data_type"] and
              res[fix + "elem_data_type"] == res[elem + "data_type"] and
              res[fix + "elem_id"] == res[elem + "id"]):
            tmp_elem["fixes"].append({"num": f,
                                      "add": expand_tags(res[fix + "tags_create"], {}),
                                      "mod": expand_tags(res[fix + "tags_modify"], {}),
                                      "del": expand_tags(res[fix + "tags_delete"], {}, True),
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
                                  "add": expand_tags(res[fix + "tags_create"], {}),
                                  "mod": expand_tags(res[fix + "tags_modify"], {}),
                                  "del": expand_tags(res[fix + "tags_delete"], {}, True),
                                 })


    response.content_type = "application/json"
    return json.dumps({
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
