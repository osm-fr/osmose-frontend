OsmoseCoverage = L.GeoJSON.extend({

  initialize: function (geojson_url, options) {
    L.Util.setOptions(this, options);

    this._layers = {};
    this._geojson_url = geojson_url;
    this._geojson = null;
  },

  onAdd: function (map, insertAtTheBottom) {
    this._map = map;
    if (this._geojson === null) {
      this.fetchData();
    }

    L.FeatureGroup.prototype.onAdd.call(this, map, insertAtTheBottom);
  },

  fetchData: function () {
    var self = this;
    this._map.spin(true);
    $.ajax({
      'url': this._geojson_url
    }).done(function (data) {
      self.addData(data);
      self._geojson = data;
    }).always(function () {
      self._map.spin(false);
    });
  },
});
