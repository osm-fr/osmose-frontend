require('leaflet');
const Pbf = require('pbf');
const topojson = require('topojson');
const geobuf = require('./geobuf-1.0.1.js');


const OsmoseCoverage = L.GeoJSON.extend({

  initialize(topojsonUrl, options) {
    L.Util.setOptions(this, options);

    this._layers = {};
    this._topojsonUrl = topojsonUrl;
    this._topojson = null;
  },

  onAdd(map, insertAtTheBottom) {
    this._map = map;
    if (this._topojson === null) {
      this.fetchData();
    }

    L.FeatureGroup.prototype.onAdd.call(this, map, insertAtTheBottom);
  },

  fetchData() {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', this._topojsonUrl, true);
    xhr.responseType = 'arraybuffer';

    xhr.onload = () => {
      if (xhr.status === 200) {
        let data = geobuf.decode(new Pbf(new Uint8Array(xhr.response)));
        data = topojson.feature(data, data.objects['osmose-cover']);
        this.addData(data);
        this._topojson = data;
      }
    };

    xhr.send();
  },
});


export { OsmoseCoverage as default };
