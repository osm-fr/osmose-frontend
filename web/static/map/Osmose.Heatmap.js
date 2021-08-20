import 'leaflet';
import 'leaflet.vectorgrid/dist/Leaflet.VectorGrid.js';


const OsmoseHeatmap = L.VectorGrid.Protobuf.extend({

  initialize(itemState, query, options) {
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

    L.VectorGrid.Protobuf.prototype.initialize.call(this, "fakeURL", vectorTileOptions);
    this.setURLQuery(query);
  },

  setURLQuery(query) {
    const newUrl = API_URL + `/api/0.3/issues/{z}/{x}/{y}.heat.mvt?${query}`;
    if (this._url !== newUrl) {
      this.setUrl(newUrl);
    }
  },
});


export { OsmoseHeatmap as default };
