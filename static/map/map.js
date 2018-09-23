import { mapBases, mapOverlay } from './layers.js';
import { OsmoseCoverage } from './Osmose.Coverage.js';
import { OsmoseMenu, OsmoseMenuToggle } from './Osmose.Menu.js';
import { OsmoseExport } from './Osmose.Export.js';
import { OsmoseEditor } from './Osmose.Editor.js';
import { OsmoseMarker } from './Osmose.Marker.js';
import { OsmoseHeatmap } from './Osmose.Heatmap.js';

require('leaflet-active-area/src/leaflet.activearea.js');
require('./Permalink.Item.js');
require('./Location.js');
require('leaflet-control-geocoder');
require('leaflet-control-geocoder/dist/Control.Geocoder.css');
require('leaflet-loading');
require('leaflet-loading/src/Control.Loading.css');
const Cookies = require('js-cookie');


export function init_map() {
  const urlVars = getUrlVars();
  urlVars.lat = urlVars.lat || Cookies.get('last_lat') || 46.97;
  urlVars.lon = urlVars.lon || Cookies.get('last_lon') || 2.75;
  urlVars.zoom = urlVars.zoom || Cookies.get('last_zoom') || 6;
  urlVars.item = urlVars.item || Cookies.get('last_item') || 'xxxx';
  urlVars.level = urlVars.level || Cookies.get('last_level') || '1';
  urlVars.tags = urlVars.tags || Cookies.get('last_tags');
  urlVars.fixable = urlVars.fixable || Cookies.get('last_fixable');

  var layers = [];
  $.each(mapBases, (name, layer) => {
    layers.push(layer);
  });

  // Map
  const map = L.map('map', {
    center: new L.LatLng(urlVars.lat, urlVars.lon),
    zoom: urlVars.zoom,
    layers: layers[0],
  }).setActiveArea('leaflet-active-area', true);

  // Editor
  const editor = new OsmoseEditor('editor', {
    position: 'right',
  });
  map.addControl(editor);

  // Permalink
  const permalink = new L.Control.Permalink({
    // layers: layers,
    text: '',
    useLocation: true,
    position: 'bottomright',
  });
  map.addControl(permalink);

  // Layers
  // // Layer Coverage
  mapOverlay.Coverage = new OsmoseCoverage('/osmose-coverage.topojson.pbf');

  // // Layer Heatmap
  mapOverlay['Osmose Issues Heatmap'] = new OsmoseHeatmap(permalink, urlVars);

  // // Layer Marker
  const featureLayer = L.layerGroup();
  map.addLayer(featureLayer);
  const osmoseLayer = new OsmoseMarker(permalink, urlVars, editor, featureLayer, remote_url_read);
  mapOverlay['Osmose Issues'] = osmoseLayer;
  editor.errors = osmoseLayer;

  // Control Layer
  var layers = L.control.layers(mapBases, mapOverlay);
  map.addControl(layers);

  // Menu
  const menu = new OsmoseMenu('menu', permalink, urlVars, {
    position: 'left',
  });
  map.addControl(menu);
  map.addControl(new OsmoseMenuToggle(menu));
  menu.show();

  // Export Menu
  new OsmoseExport(map, permalink, urlVars);

  // Widgets
  const scale = L.control.scale({
    position: 'bottomright',
  });
  map.addControl(scale);

  const location = L.control.location();
  map.addControl(location);

  const geocode = L.Control.geocoder({
    position: 'topleft',
    showResultIcons: true,
  });
  geocode.markGeocode = function (result) {
    this._map.fitBounds(result.geocode.bbox);
    return this;
  };
  map.addControl(geocode);

  const loadingControl = L.Control.loading({
    separate: true,
  });
  map.addControl(loadingControl);

  map.addLayer(osmoseLayer);

  $.ajax({
    url: $('#popupTpl').attr('src'),
  }).done((html) => {
    $('#popupTpl').html(html);
  });

  $.ajax({
    url: $('#editorTpl').attr('src'),
  }).done((html) => {
    $('#editorTpl').html(html);
  });


  function active_menu(e) {
    const zoom = map.getZoom();
    const lat = Math.abs(map.getCenter().lat);
    if (zoom >= 6 || (zoom >= 5 && lat > 60) || (zoom >= 4 && lat > 70) || (zoom >= 3 && lat > 75)) {
      $('#need_zoom').hide();
      $('#action_links, #tests').show();
    } else {
      $('#need_zoom').show();
      $('#action_links, #tests').hide();
    }
  }

  map.on('zoomend', active_menu);
  map.on('moveend', active_menu);
  active_menu();
}
