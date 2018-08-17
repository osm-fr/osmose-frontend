import { mapBases, mapOverlay } from './layers.js';
require('leaflet-active-area/src/leaflet.activearea.js');
import { OsmoseCoverage } from './Osmose.Coverage.js';
import { OsmoseMenu, OsmoseMenuToggle } from './Osmose.Menu.js';
import { OsmoseExport } from './Osmose.Export.js';
import { OsmoseEditor } from './Osmose.Editor.js';
import { OsmoseMarker } from './Osmose.Marker.js';
import { OsmoseHeatmap } from './Osmose.Heatmap.js';
require('./Permalink.Item.js');
require('./Permalink.Overlay.js');
require('./Location.js');
require('leaflet-control-geocoder');
require('leaflet-control-geocoder/dist/Control.Geocoder.css');
require('leaflet-loading');
require('leaflet-loading/src/Control.Loading.css');


export function init_map() {
  var urlVars = getUrlVars();

  var layers = [];
  $.each(mapBases, function (name, layer) {
    layers.push(layer);
  });

  var map = L.map('map', {
    center: new L.LatLng(lat, lon),
    zoom: zoom,
    layers: layers[0]
  }).setActiveArea('leaflet-active-area');
  map.setView(new L.LatLng(lat, lon));

  var coverage = new OsmoseCoverage('/osmose-coverage.topojson.pbf');
  mapOverlay['Coverage'] = coverage;

  var menu = new OsmoseMenu('menu', {
    position: 'left'
  });
  map.addControl(menu);
  map.addControl(new OsmoseMenuToggle(menu));
  menu.show();

  new OsmoseExport(map, menu);

  var editor = new OsmoseEditor('editor', {
    position: 'right'
  });
  map.addControl(editor);

  mapOverlay['Osmose Issues Heatmap'] = new OsmoseHeatmap(menu, urlVars);
  var featureLayer = L.layerGroup()
  map.addLayer(featureLayer);
  var osmoseLayer = new OsmoseMarker(menu, urlVars, editor, featureLayer, remote_url_read);
  mapOverlay['Osmose Issues'] = osmoseLayer;
  editor.errors = osmoseLayer;

  var layers = L.control.layers(mapBases, mapOverlay);
  map.addControl(layers);

  var permalink = new L.Control.Permalink({
    layers: layers,
    position: 'bottomright',
    menu: menu
  });
  map.addControl(permalink);

  var scale = L.control.scale({
    position: 'bottomright'
  });
  map.addControl(scale);

  var location = L.control.location();
  map.addControl(location);

  var geocode = L.Control.geocoder({
    position: 'topleft',
    showResultIcons: true
  });
  geocode.markGeocode = function (result) {
    this._map.fitBounds(result.geocode.bbox);
    return this;
  };
  map.addControl(geocode);

  var loadingControl = L.Control.loading({
    separate: true
  });
  map.addControl(loadingControl);

  if (!urlVars.overlays) {
    map.addLayer(osmoseLayer);
  }

  $.ajax({
    url: $("#popupTpl").attr("src")
  }).done(function (html) {
    $("#popupTpl").html(html);
  });

  $.ajax({
    url: $("#editorTpl").attr("src")
  }).done(function (html) {
    $("#editorTpl").html(html);
  });


  function active_menu(e) {
    var zoom = map.getZoom()
      lat = Math.abs(map.getCenter().lat);
    if (zoom >= 6 || (zoom >= 5 && lat > 60) || (zoom >= 4 && lat > 70) || (zoom >= 3 && lat > 75)) {
      $("#need_zoom").hide();
      $("#action_links, #tests").show();
    } else {
      $("#need_zoom").show();
      $("#action_links, #tests").hide();
    }
  }

  map.on('zoomend', active_menu);
  map.on('moveend', active_menu);
}
