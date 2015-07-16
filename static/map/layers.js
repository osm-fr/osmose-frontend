var osmAttribution = '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors';
var mapBases = {
  // OpenStreetMap
  'Mapnik': L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  'MapQuest Open': L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png', {subdomains: '123', attribution: osmAttribution + " - Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\">"}),
  'ÖPNV Karte': L.tileLayer('http://tile.memomaps.de/tilegen/{z}/{x}/{y}.png'),
  'White background': L.tileLayer('http://a.layers.openstreetmap.fr/blanc.png'),
  'Mapnik-osmfr': L.tileLayer('http://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  'HOT': L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  'Bing': L.bingLayer('AmQcQsaJ4WpRqn2_k0rEToboqaM1ind8HMmM0XwKwW9R8bChmHEbczHwjnjFpuNP', {type: 'Aerial'}),
  'MapBox Satellite': L.tileLayer('http://{s}.tiles.mapbox.com/v4/openstreetmap.map-inh7ifmo/{z}/{x}/{y}.png?access_token=pk.eyJ1Ijoib3BlbnN0cmVldG1hcCIsImEiOiJhNVlHd29ZIn0.ti6wATGDWOmCnCYen-Ip7Q'),
  // OpenGeoFiction
  //'Standard': L.tileLayer('http://opengeofiction.net/osm_tiles/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  //'TopoMap': L.tileLayer('http://opengeofiction.net/tiles-topo/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  //'histor': L.tileLayer('http://opengeofiction.net/tiles-histor/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  //'Roantra': L.tileLayer('http://opengeofiction.net/planet/Roantra/{z}/{x}/{y}.png', {attribution: osmAttribution}),
};

var urlOsmFr = 'http://{s}.layers.openstreetmap.fr/{layer}/{z}/{x}/{y}.png';
var attributionOsmFr = '';
var mapOverlay = {
  'No name': L.tileLayer(urlOsmFr, {layer: 'noname', attribution: attributionOsmFr}),
  'No Oneway': L.tileLayer(urlOsmFr, {layer: 'nooneway', attribution: attributionOsmFr}),
  'No Ref on way': L.tileLayer(urlOsmFr, {layer: 'noref', attribution: attributionOsmFr}),
  'Fixme tags': L.tileLayer(urlOsmFr, {layer: 'fixme', attribution: attributionOsmFr}),
  'Note tags': L.tileLayer(urlOsmFr, {layer: 'note', attribution: attributionOsmFr}),
  'validate:my_own=yes': L.tileLayer(urlOsmFr, {layer: 'my_own', attribution: attributionOsmFr}),
  'admin_level=4': L.tileLayer(urlOsmFr, {layer: 'admin4', attribution: attributionOsmFr}),
  'admin_level=5': L.tileLayer(urlOsmFr, {layer: 'admin5', attribution: attributionOsmFr}),
  'admin_level=6': L.tileLayer(urlOsmFr, {layer: 'admin6', attribution: attributionOsmFr}),
  'admin_level=7': L.tileLayer(urlOsmFr, {layer: 'admin7', attribution: attributionOsmFr}),
  'admin_level=8': L.tileLayer(urlOsmFr, {layer: 'admin8', attribution: attributionOsmFr}),
  'admin_level=10': L.tileLayer(urlOsmFr, {layer: 'admin10', attribution: attributionOsmFr}),
  'boundary=local_authority': L.tileLayer(urlOsmFr, {layer: 'boundary_local_authority', attribution: attributionOsmFr}),
  'boundary=political': L.tileLayer(urlOsmFr, {layer: 'boundary_political', attribution: attributionOsmFr}),
  'boundary=election': L.tileLayer(urlOsmFr, {layer: 'boundary_election', attribution: attributionOsmFr}),
  'Voirie/Cadastre': L.tileLayer(urlOsmFr, {layer: 'voirie-cadastre', attribution: attributionOsmFr}),
  'No ref without tertiary': L.tileLayer(urlOsmFr, {layer: 'noref-notertiary', attribution: attributionOsmFr}),
};
