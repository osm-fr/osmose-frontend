var osmAttribution = '&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors';
var mapBases = {
  'Mapnik': L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  'MapQuest Open': L.tileLayer('http://otile{s}.mqcdn.com/tiles/1.0.0/osm/{z}/{x}/{y}.png', {subdomains: '123', attribution: osmAttribution + " - Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\">"}),
  'ÖPNV Karte': L.tileLayer('http://tile.memomaps.de/tilegen/{z}/{x}/{y}.png'),
  'Bing': new L.BingLayer('AmQcQsaJ4WpRqn2_k0rEToboqaM1ind8HMmM0XwKwW9R8bChmHEbczHwjnjFpuNP', {type: 'Aerial'}),
  'White background': L.tileLayer('http://a.layers.openstreetmap.fr/blanc.png'),
  'Mapnik-osmfr': L.tileLayer('http://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  'HOT': L.tileLayer('http://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {attribution: osmAttribution}),
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
  'Osmose Errors Heatmap': L.tileLayer('heat/{z}/{x}/{y}.png'),
};
