import 'leaflet';
import 'leaflet.vectorgrid/dist/Leaflet.VectorGrid.js';


const OsmoseHeatmap = L.VectorGrid.Protobuf.extend({

  initialize(permalink, itemState, options) {
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

    L.VectorGrid.Protobuf.prototype.initialize.call(this, this._buildUrl(itemState), vectorTileOptions);
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
    params = Object.assign({}, params);
    delete params.lat;
    delete params.lon;
    delete params.issue_uuid;

    const query = this.params = Object.entries(params)
      .filter(([k, v]) => v !== undefined && v != null)
      .map(([k, v]) => encodeURIComponent(k) + "=" + encodeURIComponent(v))
      .join("&");

    return API_URL + `/api/0.3/issues/{z}/{x}/{y}.heat.mvt?${query}`;
  },

  _setUrl(e) {
    const newUrl = this._buildUrl(e.params);
    if (this._url !== newUrl) {
      this.setUrl(newUrl);
    }
  },
});


export { OsmoseHeatmap as default };
