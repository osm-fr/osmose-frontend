import $ from 'jquery';
import { init_map } from './map.js';
import { setCookie, getUrlVars } from './menu.js';

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
window.init_map = init_map;
window.setCookie = setCookie;
window.getUrlVars = getUrlVars;
