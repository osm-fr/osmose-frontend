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
      urlPart;
    $("#menu-export ul a").each(function (i, a) {
      urlPart = self._menu.urlPart();
      urlPart.bbox = self._map.getBounds().toBBoxString();
      a.href = a.href.split("?")[0] + L.Util.getParamString(urlPart);
    });
  },
});
