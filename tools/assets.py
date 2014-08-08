#! /usr/bin/env python
#-*- coding: utf-8 -*-

from webassets import Environment, Bundle

environment = Environment('static', '')
# environment.debug = True

css_map_bundle = Bundle(
    'css/style.css',
    'map/leaflet/leaflet.css',
    'map/leaflet-sidebar/src/L.Control.Sidebar.css',
    'map/leaflet-control-geocoder/Control.Geocoder.css',
    'map/Osmose.Editor.css',
    'map/style.css',
    'map/Osmose.Menu.css',
    filters='cssrewrite,cssmin', output='gen/map-%(version)s.css')
environment.register('css_map', css_map_bundle)

js_map_bundle = Bundle(
    'js/jquery-1.7.2.js',
    'js/jquery-ui-1.10.4.dialog.js',
    'js/mustache.js',
    'map/leaflet/leaflet-src.js',
    'map/leaflet-plugins/control/Permalink.js',
    'map/leaflet-plugins/control/Permalink.Layer.js',
    'map/Permalink.Overlay.js',
    'map/Permalink.Item.js',
    'map/leaflet-plugins/layer/tile/Bing.js',
    'map/layers.js',
    'map/leaflet.active-layers.min.js',
    'map/leaflet.select-layers.min.js',
    'map/leaflet-sidebar/src/L.Control.Sidebar.js',
    'map/leaflet-control-geocoder/Control.Geocoder.js',
    'map/leaflet-active-area/L.activearea.js',
    'map/Location.js',
    'map/Osmose.Menu.js',
    'map/Osmose.Editor.js',
    'map/Osmose.Coverage.js',
    'map/Osmose.Heatmap.js',
    'map/Osmose.Marker.js',
    'map/Osmose.Errors.js',
    'map/Osmose.Spin.js',
    'map/Osmose.Export.js',
    'map/map.js',
    'map/menu.js',
    filters='rjsmin', output='gen/map-%(version)s.js')
environment.register('js_map', js_map_bundle)
