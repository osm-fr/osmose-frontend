Mapillary = L.TileLayer.MVTSource.extend({

  _client_id: null,

  initialize: function (client_id) {
    this._client_id = client_id;
    L.TileLayer.MVTSource.prototype.initialize.call(this, {
      url: "https://d2munx5tg0hw47.cloudfront.net/tiles/{z}/{x}/{y}.mapbox",
      getIDForLayerFeature: function(feature) {
        return feature.properties.id;
      },
      zIndex: 2,
      style: function (feature) {
	return {
	  color: 'rgba(0,255,0,0.8)',
          size: 3,
	};
      }
    });
  },

  onAdd: function (map) {
    this._map = map;
    this._bind_onClick = L.Util.bind(this._onClick, this);
    map.on('click', this._bind_onClick);
    L.TileLayer.MVTSource.prototype.onAdd.call(this, map);
  },

  onRemove: function (map) {
    map.off('click', this._bind_onClick);
  },

  _onClick: function (e) {
    var self = this;
    this._ajax("https://a.mapillary.com/v2/search/im/close?client_id=" + this._client_id + "&lat=" + e.latlng.lat + "&lon=" + e.latlng.lng + "&limit=1", function(json) {
      var im = JSON.parse(json).ims[0];
      //[{"ca":164.309981822046,"captured_at":1423158021000,"distance":26.849678599,"key":"zr9Yl7eYCmUm-FtpO6EmRg","lon":2.33909010887146,"lat":48.8530414830134,"location":"Paris","user":"dhuyp"}]}
      var popup = L.popup()
        .setLatLng([im.lat, im.lon])
        .setContent("<a href='http://www.mapillary.com/map/im/" + im.key + "/photo' target='_blank'><img src='https://d1cuyjsrcm0gby.cloudfront.net/" + im.key+ "/thumb-320.jpg' width='240' /></br>" + im.user + " - Mapillary - CC BY-SA 4.0</a>")
        .openOn(self._map);
    });
  },

  _ajax: function (url, callback) {
    var self = this;

    var xhr = new XMLHttpRequest();
    xhr.open('GET', url, true);
    xhr.onload = function(e) {
      if (this.status == 200) {
	callback(xhr.response);
      }
    };

    xhr.send();
  },
});
