require('leaflet');


const OsmoseExport = L.Class.extend({

  _map: null,

  initialize(map, permalink, params) {
    this._map = map;
    permalink.on('update', this._setUrl, this);
    this._setUrl({ params });
  },

  _setUrl(e) {
    const params = Object.assign({}, e.params);
    params.limit = 500;
    params.bbox = this._map.getBounds().toBBoxString();
    $('#menu-export ul a').each((i, a) => {
      a.href = $(a).data('href') + L.Util.getParamString(params);
    });
  },
});


export { OsmoseExport as default };
