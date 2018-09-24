require('leaflet.vectorgrid/dist/Leaflet.VectorGrid.js');


export const Mapillary = L.VectorGrid.Protobuf.extend({

  _client_id: null,

  initialize(clientId) {
    this._clientId = clientId;
    L.VectorGrid.Protobuf.prototype.initialize.call(this, 'https://d2munx5tg0hw47.cloudfront.net/tiles/{z}/{x}/{y}.mapbox', {
      getIDForLayerFeature(feature) {
        return feature.properties.id;
      },
      zIndex: 2,
      vectorTileLayerStyles: {
        'mapillary-sequences': {
          color: 'rgba(0,255,0,0.8)',
          weight: 3,
        },
      },
    });
  },

  onAdd(map) {
    this._map = map;
    L.VectorGrid.Protobuf.prototype.onAdd.call(this, map);
    this._onClick_bind = L.Util.bind(this._onClick, this);
    map.on('click', this._onClick_bind);
  },

  onRemove(map) {
    L.VectorGrid.Protobuf.prototype.onRemove.call(this, map);
    map.off('click', this._onClick_bind);
  },

  _onClick(e) {
    const self = this;
    this._ajax(`https://a.mapillary.com/v2/search/im/close?client_id=${this._clientId}&lat=${e.latlng.lat}&lon=${e.latlng.lng}&limit=1`, (json) => {
      const im = JSON.parse(json).ims[0];
      // [{"ca":164.309981822046,"captured_at":1423158021000,"distance":26.849678599,"key":"zr9Yl7eYCmUm-FtpO6EmRg","lon":2.33909010887146,"lat":48.8530414830134,"location":"Paris","user":"dhuyp"}]}
      L.responsivePopup()
        .setLatLng([im.lat, im.lon])
        .setContent(`<a href='http://www.mapillary.com/map/im/${im.key}/photo' target='_blank'><img src='https://d1cuyjsrcm0gby.cloudfront.net/${im.key}/thumb-320.jpg' width='240' /></br>${im.user} - Mapillary - CC BY-SA 4.0</a>`)
        .openOn(self._map);
    });
  },

  _ajax(url, callback) {
    const xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onload = function (e) {
      if (this.status == 200) {
        callback(xhr.response);
      }
    };

    xhr.send();
  },
});
