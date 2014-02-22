OsmoseHeatmap = L.TileLayer.extend({

  _options: null,

  _menu: null,

  initialize: function (menu, options) {
    this._menu = menu;
    L.TileLayer.prototype.initialize.call(this, this._makeUrl(), options);
  },

  onAdd: function (map) {
    L.TileLayer.prototype.onAdd.call(this, map);
    this._menu.on('itemchanged', this._setUrl, this);
  },

  onRemove: function (map) {
    this._menu.off('itemchanged', this._setUrl, this);
    L.TileLayer.prototype.onRemove.call(this, map);
  },

  _makeUrl: function () {
    var urlPart = this._menu.urlPart(),
      params = {
        item: urlPart.item,
        level: urlPart.level,
      },
      url = L.Util.getParamString(params);

    return 'heat/{z}/{x}/{y}.png' + url;
  },

  _setUrl: function () {
    this.setUrl(this._makeUrl());
  },
});
