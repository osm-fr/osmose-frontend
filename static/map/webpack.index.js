import $ from 'jquery';
import { initMap } from './map';

require('../css/style.css');
require('./style.css');
require('../images/markers/markers-l.css');

require('leaflet');
require('leaflet/dist/leaflet.css');

require('bootstrap');
require('bootstrap/dist/css/bootstrap.css');

// Retro-compact hack for Leaflet.VectorGrid
L.DomEvent.fakeStop = L.DomEvent._fakeStop;
window.$ = $;
window.initMap = initMap;
