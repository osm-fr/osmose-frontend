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
from modules import utils
from modules.utils import i10n_select_auto
from modules.params import Params
from modules import query
from modules import query_meta
from collections import defaultdict
from lxml import etree
from lxml.builder import E, ElementMaker
import io, re, csv

from . import errors_graph


def int_list(s):
    return list(map(lambda x: int(x), filter(lambda x: x and x!='',s)).split(','))

@route('/issues/graph.<format:ext>')
def graph(db, format='png'):
    try:
        data = errors_graph.make_plt(db, Params(), format)
        response.content_type = {'png':'image/png', 'svg':'image/svg+xml', 'pdf':'application/pdf', 'csv':'text/csv', 'json':'application/json'}[format]
        return data
    except Exception as e:
        response.content_type = "text/plain"
        import traceback
        out = io.StringIO()
        traceback.print_exc(file=out)
        return out.getvalue() + "\n"


@route('/issues/open.<format:ext>')
@route('/issues/done.<format:ext>')
@route('/issues/false-positive.<format:ext>')
def index(db, lang, format):
    if "false-positive" in request.path:
        title = _("False positives")
        gen = "false-positive"
    elif "done" in request.path:
        title = _("Fixed issues")
        gen = "done"
    else:
        title = _("Open issues")
        gen = "issue"

    params = Params()
    params.status = {"issue":"open", "false-positive": "false", "done":"done"}[gen]
    params.fixable = None

    items = query_meta._items_menu(db, lang)
    for res in items:
        if params.item == str(res["item"]):
            title += ' - ' + res['menu']['auto']

    params.limit = request.params.get('limit', type=int, default=100)
    if params.limit > 10000:
        params.limit = 10000

    params.full = True
    errors = query._gets(db, params)
    for error in errors:
        error["subtitle"] = i10n_select_auto(error["subtitle"], lang)
        error["title"] = i10n_select_auto(error["title"], lang)
        error["menu"] = i10n_select_auto(error["menu"], lang)

    if format == 'rss':
        response.content_type = 'application/rss+xml'
        xml = rss(title=title, website=utils.website, lang=lang[0], params=params, query=request.query_string, main_website=utils.main_website, remote_url_read=utils.remote_url_read, issues=errors)
        return etree.tostring(xml, pretty_print=True)
    elif format == 'gpx':
        response.content_type = 'application/gpx+xml'
        xml = gpx(title=title, website=utils.website, lang=lang[0], params=params, query=request.query_string, main_website=utils.main_website, remote_url_read=utils.remote_url_read, issues=errors)
        return etree.tostring(xml, pretty_print=True)
    elif format == 'kml':
        response.content_type = 'application/vnd.google-earth.kml+xml'
        xml = kml(title=title, website=utils.website, lang=lang[0], params=params, query=request.query_string, main_website=utils.main_website, remote_url_read=utils.remote_url_read, issues=errors)
        return etree.tostring(xml, pretty_print=True)
    elif format == 'josm':
        objects = set(sum(map(lambda error: list(map(lambda elem: elem['type'].lower() + str(elem['id']), error['elems'] or [])), errors), []))
        response.status = 302
        response.set_header('Location', 'http://localhost:8111/load_object?objects=%s' % ','.join(objects))
        return
    elif format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        h = ['uuid', 'source', 'item', 'class', 'level', 'title', 'subtitle', 'country', 'analyser', 'timestamp', 'username', 'lat', 'lon', 'elems']
        hh = {'source': 'source_id'}
        writer.writerow(h)
        for res in errors:
            usernames = list(map(lambda elem: elem.get("username", ""), res['elems'] or []))
            elems = '_'.join(map(lambda elem: {'N':'node', 'W':'way', 'R':'relation'}[elem['type']] + str(elem['id']), res['elems'] or []))
            writer.writerow(list(map(lambda a: usernames if a == 'username' else elems if a == 'elems' else res[a], map(lambda y: hh.get(y, y), h))))
        response.content_type = 'text/csv'
        return output.getvalue()
    else:
        countries = query_meta._countries(db)
        items = list(map(dict, items))

        if params.item:
            params.limit = None
            errors_groups = query._count(db, params, [
                "markers_counts.item",
                "markers.source_id",
                "markers.class",
                "sources.country",
                "sources.analyser",
                "updates_last.timestamp"], [
                "items",
                "class"], [
                "min(items.menu::text)::jsonb AS menu",
                "min(class.title::text)::jsonb AS title"],
            )

            total = 0
            for res in errors_groups:
                res["title"] = i10n_select_auto(res["title"], lang)
                res["menu"] = i10n_select_auto(res["menu"], lang)
                if res["count"] != -1:
                    total += res["count"]
        else:
            errors_groups = []
            total = 0

        if gen in ("false-positive", "done"):
            opt_date = "date"
        else:
            opt_date = None

        errors_groups = list(map(dict, errors_groups))
        for res in errors_groups:
            res['timestamp'] = str(res['timestamp'])
        errors = list(map(dict, errors))
        for res in errors:
            res['timestamp'] = str(res['timestamp'])
            if 'date' in res:
                res['date'] = str(res['date'])
        return dict(countries=countries, items=items, errors_groups=errors_groups, total=total, errors=errors, gen=gen, opt_date=opt_date, website=utils.website, main_website=utils.main_website, remote_url_read=utils.remote_url_read)


@route('/issues/matrix.json')
def matrix(db, lang):
    params = Params(default_limit=None)
    errors_groups = query._count(db, params, [
        "markers.item",
        "markers.class",
        "sources.country",
        "items.menu->'en'"]
    )
    analysers = defaultdict(lambda: defaultdict(int))
    analysers_sum = defaultdict(int)
    countries_sum = defaultdict(int)
    total = 0
    for row in errors_groups:
        item, class_, country, menu, count = row
        analyser = '{}/{} {}'.format(item, class_, menu)
        analysers[analyser][country] += count
        analysers_sum[analyser] += count
        countries_sum[country] += count
        total += count

    return dict(total=total, countries_sum=countries_sum, analysers_sum=analysers_sum, analysers=analysers)


def xml_header(params, title, website, lang, query):
    if params.users:
        title = 'Osmose - ' + ', '.join(params.users)
        description = _("Statistics for user {}").format(', '.join(params.users))
        url = 'http://{}/byuser/{}'.format(website, ', '.join(params.users))
    else:
        title = 'Osmose - ' + title
        description = None
        url = 'http://{}/{}/issues/open?{}'.format(website, lang, query)
    return title, description, url


def xml_issue(res, website, lang, query, main_website, remote_url_read):
    name = (res['menu'] or '') + ' - ' + (res['subtitle'] or res['title'] or '')

    lat = res['lat']
    lon = res['lon']

    map_url = 'http://{}/{}/map/#{}&amp;zoom=16&amp;lat={}&amp;lon={}&amp;level={}&amp;tags=&amp;fixable=&amp;issue_uuid={}'.format(website, lang, query, lat, lon, res["level"], res["uuid"])

    desc = '{}({})/{} {}'.format(res["item"], res["level"], res["class"], res["uuid"])
    if res['elems']:
        for e in res['elems']:
            desc += ' {}{}/{}'.format(main_website, e["type_long"], e["id"])
            if e['type'] == 'R':
                desc += ' http://localhost:8111/import?url={}api/0.6/relation/{}/full'.format(remote_url_read, e["id"])
            else:
                desc += ' http://localhost:8111/load_object?objects={}{}'.format(e["type"].lower(), e["id"])
    else:
        minlat = float(lat) - 0.002
        maxlat = float(lat) + 0.002
        minlon = float(lon) - 0.002
        maxlon = float(lon) + 0.002
        desc += ' http://localhost:8111/load_and_zoom?left={}&amp;bottom={}&amp;right={}&amp;top={}'.format(minlon, minlat, maxlon, maxlat)

    return lat, lon, name, desc, map_url


def gpx_issue(res, website, lang, query, main_website, remote_url_read):
    lat, lon, name, desc, map_url = xml_issue(res, website, lang, query, main_website, remote_url_read)
    return E.wpt(
        E.name(name),
        E.desc(desc),
        E.url(map_url),
        lat=str(lat),
        lon=str(lon),
    )

def gpx(website, lang, params, query, main_website, remote_url_read, issues, title = None):
    content = []
    if len(issues) > 0:
        content.append(E.time(issues[0]['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ')))
    content += list(map(lambda issue: gpx_issue(issue, website, lang, query, main_website, remote_url_read), issues))

    title, _, url = xml_header(params, title, website, lang, query)
    return E.gpx(
        E.name(title),
        E.url(url),
        *content,
        version = '1.0',
        creator = 'http://osmose.openstreetmap.fr',
        xmlns = 'http://www.topografix.com/GPX/1/0',
        # xmlns:xsi = 'http://www.w3.org/2001/XMLSchema-instance',
        # xsi:schemaLocation = 'http://www.topografix.com/GPX/1/0 http://www.topografix.com/GPX/1/0/gpx.xsd',
    )


def kml_issue(res, website, lang, query, main_website, remote_url_read):
    lat, lon, name, desc, map_url = xml_issue(res, website, lang, query, main_website, remote_url_read)
    return E.Placemark(
        E.name(name),
        E.url(map_url),
        E.description(desc),
        E.styleUrl('#placemark-purple'),
        E.Point(
            E.coordinates('{},{}'.format(lon, lat)),
        ),
    )

def kml(website, lang, params, query, main_website, remote_url_read, issues, title = None):
    content = map(lambda issue: kml_issue(issue, website, lang, query, main_website, remote_url_read), issues)

    title, _, url = xml_header(params, title, website, lang, query)
    if len(issues) > 0:
        title += ' (' + issues[0]['timestamp'].strftime('%Y-%m-%dT%H:%M:%SZ') + ')'
    return E.kml(
        E.Document(
            E.Style(
                E.IconStyle(
                    E.Icon(
                        E.href('http://maps.me/placemarks/placemark-purple.png')
                    ),
                ),
                id = 'placemark-purple'
            ),
            E.name(title),
            E.url(url),
        ),
        *content,
        xmlns = 'http://www.opengis.net/kml/2.2',
    )


def rss_issue(res, website, lang, query, main_website, remote_url_read):
    _, _, name, desc, map_url = xml_issue(res, website, lang, query, main_website, remote_url_read)
    return E.item(
        E.title(name),
        E.description(desc),
        E.category(str(res['item'])),
        E.link(map_url),
        E.guid(res['uuid']),
    )

def rss(website, lang, params, query, main_website, remote_url_read, issues, title = None):
    content = map(lambda issue: rss_issue(issue, website, lang, query, main_website, remote_url_read), issues)

    lastBuildDate = []
    if len(issues) > 0:
        time = issues[0]['timestamp']
        ctime = time.ctime()
        rfc822 = '{0}, {1:02d} {2}'.format(ctime[0:3], time.day, ctime[4:7]) + time.strftime(' %Y %H:%M:%S %z')
        lastBuildDate = [E.lastBuildDate(rfc822)]

    title, description, url = xml_header(params, title, website, lang, query)
    E_atom = ElementMaker(namespace='http://www.w3.org/2005/Atom', nsmap={'atom':'http://www.w3.org/2005/Atom'})
    return E.rss(
        E.channel(
            E_atom.link(
                href='http://{}/{}/issues/open.rss?{}'.format(website, lang, query),
                rel='self',
                type='application/rss+xml',
            ),
            E.title(title),
            E.description(description or query),
            *lastBuildDate,
            E.link(url),
            *content,
        ),
        version = '2.0',
    )
