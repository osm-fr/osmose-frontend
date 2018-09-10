require('leaflet');


export var OsmoseExport = L.Class.extend({

  _map: null,

  initialize: function (map, permalink, params) {
    this._map = map;
    permalink.on('update', this._setUrl, this);
    this._setUrl({params: params});
  },

  _setUrl: function (e) {
    var params = Object.assign({}, e.params);
    params.limit = 500;
    params.bbox = this._map.getBounds().toBBoxString();
    $("#menu-export ul a").each(function (i, a) {
      a.href = $(a).data('href') + L.Util.getParamString(params);
    });
  },
});
