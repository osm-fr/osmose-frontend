
require('../css/style.css');
require('./style.css');
require('../images/markers/markers-l.css');

require('leaflet');
require('leaflet/dist/leaflet.css');

// Retro-compact hack for Leaflet.VectorGrid
L.DomEvent.fakeStop = L.DomEvent._fakeStop;

import $ from 'jquery';
window.$ = $;

import { init_map } from './map.js';
window.init_map = init_map;

import { setCookie, set_lang, getUrlVars } from './menu.js';
window.setCookie = setCookie;
window.set_lang = set_lang;
window.getUrlVars = getUrlVars;
