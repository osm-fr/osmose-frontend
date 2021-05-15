import 'leaflet';


const OsmoseExport = L.Class.extend({

  _map: null,

  _params_last: {},

  initialize(map, permalink, params) {
    this._map = map;
    permalink.on('update', this._setUrl, this);
    map.on('moveend', (e) => {
      this._setUrl({ params: this._params_last });
    });
    this._params_last = params;
    this._setUrl({ params });
  },

  _setUrl(e) {
    const params = Object.assign({}, e.params);
    delete params.lat;
    delete params.lon;
    delete params.issue_uuid;
    this._params_last = params;
    params.limit = 500;
    params.bbox = this._map.getBounds().toBBoxString();
    Object.keys(params).forEach(key => {
      if (params[key] === undefined) {
        delete params[key];
      }
    });
    Object.values(document.getElementsByClassName("menu-export")).forEach((a) => {
      a.href = a.dataset.href + L.Util.getParamString(params);
    });
  },
});


export { OsmoseExport as default };
