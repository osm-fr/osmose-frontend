OsmoseErrors = L.LayerGroup.extend({

  _menu: null,

  _params: {},

  _editor: null,

  _onMap: false,

  _osmoseMarker: null,

  initialize: function (menu, params, editor) {
    L.LayerGroup.prototype.initialize.call(this);
    this._menu = menu;
    this._params = params;
    this._editor = editor;
  },

  onAdd: function (map) {
    this._map = map;
    this._onMap = true;
    this._osmoseMarker = new OsmoseMarker(this._getUrl(), this._editor);
    this.addLayer(this._osmoseMarker);
    this._menu.on('itemchanged', this._updateOsmoseLayer, this);
  },

  onRemove: function (map) {
    this._menu.off('itemchanged', this._updateOsmoseLayer, this);
    this._onMap = false;
    this.clearLayers();
  },

  _getUrl: function() {
    var urlPart = this._menu.urlPart();
    if (urlPart.item) {
      this._params.item = urlPart.item;
    } else {
      delete this._params.item;
    }
    if (urlPart.level) {
      this._params.level = urlPart.level;
    } else {
      delete this._params.level;
    }
    if (urlPart.tags) {
      this._params.tags = urlPart.tags;
    } else {
      delete this._params.tags;
    }
    if (urlPart.fixable) {
      this._params.fixable = urlPart.fixable;
    } else {
      delete this._params.fixable;
    }
    return L.Util.getParamString(this._params);
  },

  _updateOsmoseLayer: function () {
    if (this._map.getZoom() >= 6) {
      this._osmoseMarker.setUrl('./issues/{z}/{x}/{y}.mvt' + this._getUrl());
    }
  },

  corrected: function (layer) {
    this._osmoseMarker.corrected(layer);
  },
});
