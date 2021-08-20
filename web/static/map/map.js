import { mapBases, mapOverlay } from './layers';
import OsmoseMarker from './Osmose.Marker';
import OsmoseHeatmap from './Osmose.Heatmap';

import 'leaflet-active-area/src/leaflet.activearea.js';
import './Permalink.Item.js';
import './Location.js';
import 'leaflet-control-geocoder/src/index.js';
import 'leaflet-control-geocoder/Control.Geocoder.css';
import 'leaflet-loading';
import 'leaflet-loading/src/Control.Loading.css';

export function initMap(itemState, mapState) {
  const layers = [];
  Object.values(mapBases).forEach((layer) => {
    layers.push(layer);
  });

  // Map
  const map = L.map('map', {
    center: new L.LatLng(mapState.lat, mapState.lon),
    zoom: mapState.zoom,
    layers: layers[0],
    worldCopyJump: true,
  }).setActiveArea('leaflet-active-area', true);

  // Permalink
  const permalink = new L.Control.Permalink({
    // layers: layers,
    text: '',
    useLocation: true,
    position: 'bottomright',
  });
  map.addControl(permalink);

  // Layers
  // // Layer Heatmap
  mapOverlay['Osmose Issues Heatmap'] = new OsmoseHeatmap(itemState);

  // // Layer Marker
  const featureLayer = L.layerGroup();
  map.addLayer(featureLayer);
  const osmoseLayerMarker = new OsmoseMarker(permalink, mapState, itemState, doc, featureLayer, remoteUrlRead);
  mapOverlay['Osmose Issues'] = osmoseLayerMarker;

  // Control Layer
  const controlLayers = L.control.layers(mapBases, mapOverlay);
  map.addControl(controlLayers);

  // Widgets
  const scale = L.control.scale({
    position: 'bottomleft',
  });
  map.addControl(scale);

  const location = L.control.location();
  map.addControl(location);

  const geocode = L.Control.geocoder({
    position: 'topleft',
    showResultIcons: true,
  });
  geocode.markGeocode = function(result) {
    this._map.fitBounds(result.geocode.bbox);
    return this;
  };
  map.addControl(geocode);

  const loadingControl = L.Control.loading({
    separate: true,
  });
  map.addControl(loadingControl);

  map.addLayer(osmoseLayerMarker);

  return [map, osmoseLayerMarker, permalink];
}

export { initMap as default };
