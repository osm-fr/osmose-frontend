OsmoseExport = L.Class.extend({
  includes: L.Mixin.Events,

  _menu: null,

  _map: null,

  initialize: function (map, menu) {
    this._map = map;
    this._map.on('moveend', this._setUrl, this);
    this._menu = menu;
    this._menu.on('itemchanged', this._setUrl, this);
    this._setUrl();
  },

  _setUrl: function (e) {
    var self = this,
      urlPart = self._menu.urlPart();
    urlPart.bbox = self._map.getBounds().toBBoxString();
    $("#menu-export ul a").each(function (i, a) {
      a.href = a.href + L.Util.getParamString(urlPart);
    });
    delete urlPart.bbox;
  },
});
