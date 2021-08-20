import { mapBases, mapOverlay } from './layers';
import OsmoseMarker from './Osmose.Marker';
import OsmoseHeatmap from './Osmose.Heatmap';

import 'leaflet-active-area/src/leaflet.activearea.js';
import './Location.js';
import 'leaflet-control-geocoder/src/index.js';
import 'leaflet-control-geocoder/Control.Geocoder.css';
import 'leaflet-loading';
import 'leaflet-loading/src/Control.Loading.css';

export default function initMap(itemState, mapState, tileQuery) {
  // Layers
  const markerLayer = new OsmoseMarker(mapState, itemState, tileQuery, remoteUrlRead);
  mapOverlay['Osmose Issues'] = markerLayer;

  const heatmapLayer = new OsmoseHeatmap(itemState, tileQuery);
  mapOverlay['Osmose Issues Heatmap'] = heatmapLayer

  // Map
  const map = L.map('map', {
    center: new L.LatLng(mapState.lat, mapState.lon),
    zoom: mapState.zoom,
    layers: [mapBases['carto'], markerLayer],
    worldCopyJump: true,
  }).setActiveArea('leaflet-active-area', true);

  // Control Layer
  map.addControl(L.control.layers(mapBases, mapOverlay));

  // Widgets

  map.addControl(L.control.scale({
    position: 'bottomleft',
  }));

  map.addControl(L.control.location());

  const geocode = L.Control.geocoder({
    position: 'topleft',
    showResultIcons: true,
  });
  geocode.markGeocode = function (result) {
    this._map.fitBounds(result.geocode.bbox);
    return this;
  };
  map.addControl(geocode);

  map.addControl(L.Control.loading({
    separate: true,
  }));

  return [map, markerLayer, heatmapLayer];
}
