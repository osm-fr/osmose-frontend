#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frederic Rodrigo 2020                                      ##
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

def ext_filter(config):
    regexp = r'html|json|geojson|xml|rss|png|svg|pdf|gpx|kml|josm|csv|mvt'
    def to_python(match):
        return match if match in ('html', 'json', 'geojson', 'xml', 'rss', 'png', 'svg', 'pdf', 'gpx', 'kml', 'josm', 'csv', 'mvt') else 'html'
    def to_url(ext):
        return ext
    return regexp, to_python, to_url


def uuid_filter(config):
    regexp = r'[0-9a-fA-F]{8}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{4}\-[0-9a-fA-F]{12}'
    def to_python(match):
        return match
    def to_url(ext):
        return ext
    return regexp, to_python, to_url


def inspect_routes(app):
    for route in app.routes:
        if 'mountpoint' in route.config:
            prefix = route.config['mountpoint.prefix']
            subapp = route.config['mountpoint.target']

            p = prefix.split('/', 2)[1]
            if not (len(p) == 2 or (len(p) == 5 and p[2] == '_')) or p == 'en':
                for prefixes, route in inspect_routes(subapp):
                    yield [prefix] + prefixes, route
        else:
            yield [], route
