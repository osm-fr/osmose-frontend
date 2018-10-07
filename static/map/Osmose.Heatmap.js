require('leaflet');
require('leaflet.vectorgrid/dist/Leaflet.VectorGrid.js');


const OsmoseHeatmap = L.VectorGrid.Protobuf.extend({

  initialize(permalink, params, options) {
    this._permalink = permalink;

    const vectorTileOptions = {
      vectorTileLayerStyles: {
        issues(properties, zoom) {
          const color = `#${(properties.color + 0x1000000).toString(16).substr(-6)}`;
          return {
            stroke: false,
            fillColor: color,
            fillOpacity: zoom < 13 ? 0.25 + properties.count / 256 * 0.75 : 1,
            fill: true,
          };
        },
      },
    };

    L.VectorGrid.Protobuf.prototype.initialize.call(this, this._buildUrl(params), vectorTileOptions);
  },

  onAdd(map) {
    L.TileLayer.prototype.onAdd.call(this, map);
    this._permalink.on('update', this._setUrl, this);
  },

  onRemove(map) {
    this._permalink.off('update', this._setUrl, this);
    L.TileLayer.prototype.onRemove.call(this, map);
  },

  _buildUrl(params) {
    const p = ['level', 'fix', 'tags', 'item', 'class', 'fixable', 'useDevItem', 'source', 'username', 'country'].reduce((o, k) => {
      if (params[k] !== undefined) {
        o[k] = params[k];
      }
      return o;
    }, {});
    return `heat/{z}/{x}/{y}.mvt${L.Util.getParamString(p)}`;
  },

  _setUrl(e) {
    const newUrl = this._buildUrl(e.params);
    if (this._url !== newUrl) {
      this.setUrl(newUrl);
    }
  },
});


export { OsmoseHeatmap as default };
