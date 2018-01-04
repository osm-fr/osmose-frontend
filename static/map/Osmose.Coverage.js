require('leaflet');
var Pbf = require('pbf');
var geobuf = require('./geobuf-1.0.1.js');
var topojson = require('topojson');


export var OsmoseCoverage = L.GeoJSON.extend({

  initialize: function (topojson_url, options) {
    L.Util.setOptions(this, options);

    this._layers = {};
    this._topojson_url = topojson_url;
    this._topojson = null;
  },

  onAdd: function (map, insertAtTheBottom) {
    this._map = map;
    if (this._topojson === null) {
      this.fetchData();
    }

    L.FeatureGroup.prototype.onAdd.call(this, map, insertAtTheBottom);
  },

  fetchData: function () {
    var self = this;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', this._topojson_url, true);
    xhr.responseType = 'arraybuffer';

    xhr.onload = function(e) {
      if (this.status == 200) {
        var data = geobuf.decode(new Pbf(new Uint8Array(xhr.response)));
        data = topojson.feature(data, data.objects['osmose-cover']);
        self.addData(data);
        self._topojson = data;
      }
    };

    xhr.send();
  },
});
