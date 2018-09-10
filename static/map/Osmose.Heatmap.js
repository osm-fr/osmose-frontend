require('leaflet');
require('leaflet.vectorgrid/dist/Leaflet.VectorGrid.js');


export var OsmoseHeatmap = L.VectorGrid.Protobuf.extend({

  initialize: function (permalink, params, options) {
    this._permalink = permalink;

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

    L.VectorGrid.Protobuf.prototype.initialize.call(this, this._buildUrl(params), vectorTileOptions);
  },

  onAdd: function (map) {
    L.TileLayer.prototype.onAdd.call(this, map);
    this._permalink.on('update', this._setUrl, this);
  },

  onRemove: function (map) {
    this._permalink.off('update', this._setUrl, this);
    L.TileLayer.prototype.onRemove.call(this, map);
  },

  _buildUrl: function (params) {
    var p = ['level', 'fix', 'tags', 'item', 'class', 'fixable', 'useDevItem', 'source', 'username', 'country'].reduce(function(o, k) {
      if (params[k] !== undefined) {
        o[k] = params[k];
      }
      return o;
    }, {});
    return 'heat/{z}/{x}/{y}.mvt' + L.Util.getParamString(p);
  },

  _setUrl: function (e) {
    var newUrl = this._buildUrl(e.params);
    if (this._url != newUrl) {
      this.setUrl(newUrl);
    }
  }
});
