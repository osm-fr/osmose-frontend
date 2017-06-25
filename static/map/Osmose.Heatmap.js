OsmoseHeatmap = L.VectorGrid.Protobuf.extend({

  _options: null,

  _menu: null,

  _params: null,

  initialize: function (menu, params, options) {
    this._menu = menu;
    this._params = params;

    var vectorTileOptions = {
      vectorTileLayerStyles: {
        issues: function(properties, zoom) {
          var color = '#' + (properties.color + 0x1000000).toString(16).substr(-6);
          return {
            stroke: false,
            fillColor: color,
            fillOpacity: zoom < 13 ? 0.25 + properties.count / 256 * 0.75 : 1,
            fill: true,
          };
        }
      }
    };

    L.VectorGrid.Protobuf.prototype.initialize.call(this, this._makeUrl(), vectorTileOptions);
  },

  onAdd: function (map) {
    L.TileLayer.prototype.onAdd.call(this, map);
    this._menu.on('itemchanged', this._setUrl, this);
  },

  onRemove: function (map) {
    this._menu.off('itemchanged', this._setUrl, this);
    L.TileLayer.prototype.onRemove.call(this, map);
  },

  _makeUrl: function () {
    var urlPart = this._menu.urlPart(),
      params = {
        item: urlPart.item,
        level: urlPart.level,
      };
    if (this._params.class) {
      params.class = this._params.class;
    }
    var url = L.Util.getParamString(params);

    return 'heat/{z}/{x}/{y}.mvt' + url;
  },

  _setUrl: function () {
    // setUrl is not implemented
    // https://github.com/Leaflet/Leaflet.VectorGrid/issues/49
    // https://github.com/Leaflet/Leaflet.VectorGrid/pull/105
    this._url = this._makeUrl();
    this.redraw();
  },
});
