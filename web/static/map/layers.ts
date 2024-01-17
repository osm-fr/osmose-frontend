import L from 'leaflet'

import Mapillary from './Mapillary'

import 'leaflet-plugins/layer/tile/Bing'

const osmAttribution =
  '&copy <a href="https://openstreetmap.org/copyright">OpenStreetMap</a> contributors'
export const mapBases = {
  // OpenStreetMap
  carto: L.tileLayer('//tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: osmAttribution,
  }),
  CyclOSM: L.tileLayer(
    '//a.tile-cyclosm.openstreetmap.fr/cyclosm/{z}/{x}/{y}.png',
    { attribution: osmAttribution }
  ),
  'ÖPNV Karte': L.tileLayer('http://tile.memomaps.de/tilegen/{z}/{x}/{y}.png'),
  'White background': L.tileLayer('//tile.openstreetmap.org/3/4/7.png'),
  'carto-de': L.tileLayer('//tile.openstreetmap.de/{z}/{x}/{y}.png', {
    attribution: osmAttribution,
  }),
  'carto-fr': L.tileLayer('//a.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png', {
    attribution: osmAttribution,
  }),
  HOT: L.tileLayer('//tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    attribution: osmAttribution,
  }),
  Bing: L.bingLayer(
    'AmQcQsaJ4WpRqn2_k0rEToboqaM1ind8HMmM0XwKwW9R8bChmHEbczHwjnjFpuNP',
    { type: 'Aerial' }
  ),
  'MapBox Satellite': L.tileLayer(
    '//a.tiles.mapbox.com/v4/mapbox.satellite/{z}/{x}/{y}.jpg?access_token=pk.eyJ1IjoiZnJvZHJpZ28iLCJhIjoiY2tza2x2YWQxMGE2djJvcG51emw4a3lzdCJ9.0Uy0TXwxjwFaMwD9phimPQ'
  ),
  // OpenGeoFiction
  // 'Standard': L.tileLayer('http://opengeofiction.net/osm_tiles/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  // 'TopoMap': L.tileLayer('http://opengeofiction.net/tiles-topo/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  // 'histor': L.tileLayer('http://opengeofiction.net/tiles-histor/{z}/{x}/{y}.png', {attribution: osmAttribution}),
  // 'Roantra': L.tileLayer('http://opengeofiction.net/planet/Roantra/{z}/{x}/{y}.png', {attribution: osmAttribution}),
}

const urlOsmFr = 'http://a.layers.openstreetmap.fr/{layer}/{z}/{x}/{y}.png'
const attributionOsmFr = ''
export const mapOverlay = {
  'No name': L.tileLayer(urlOsmFr, {
    layer: 'noname',
    attribution: attributionOsmFr,
  }),
  'No Oneway': L.tileLayer(urlOsmFr, {
    layer: 'nooneway',
    attribution: attributionOsmFr,
  }),
  'No Ref on way': L.tileLayer(urlOsmFr, {
    layer: 'noref',
    attribution: attributionOsmFr,
  }),
  'Fixme tags': L.tileLayer(urlOsmFr, {
    layer: 'fixme',
    attribution: attributionOsmFr,
  }),
  'admin_level=4': L.tileLayer(urlOsmFr, {
    layer: 'admin4',
    attribution: attributionOsmFr,
  }),
  'admin_level=5': L.tileLayer(urlOsmFr, {
    layer: 'admin5',
    attribution: attributionOsmFr,
  }),
  'admin_level=6': L.tileLayer(urlOsmFr, {
    layer: 'admin6',
    attribution: attributionOsmFr,
  }),
  'admin_level=7': L.tileLayer(urlOsmFr, {
    layer: 'admin7',
    attribution: attributionOsmFr,
  }),
  'admin_level=8': L.tileLayer(urlOsmFr, {
    layer: 'admin8',
    attribution: attributionOsmFr,
  }),
  'admin_level=10': L.tileLayer(urlOsmFr, {
    layer: 'admin10',
    attribution: attributionOsmFr,
  }),
  'boundary=local_authority': L.tileLayer(urlOsmFr, {
    layer: 'boundary_local_authority',
    attribution: attributionOsmFr,
  }),
  'boundary=political': L.tileLayer(urlOsmFr, {
    layer: 'boundary_political',
    attribution: attributionOsmFr,
  }),
  'boundary=election': L.tileLayer(urlOsmFr, {
    layer: 'boundary_election',
    attribution: attributionOsmFr,
  }),
  Mapillary: new Mapillary(
    'MEpmMTFQclBTUWlacjV6RTUxWWMtZzo5OTc2NjY2MmRiMDUwYmMw'
  ),
}
