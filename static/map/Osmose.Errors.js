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
    this._menu.on('itemchanged', this._updateOsmoseLayer, this);
    this._onMap = true;
    this._updateOsmoseLayer();
  },

  onRemove: function (map) {
    this._menu.off('itemchanged', this._updateOsmoseLayer, this);
    this._onMap = false;
    this.clearLayers();
  },

  _updateOsmoseLayer: function () {
    if (this._map.getZoom() >= 6) {
      var urlPart = this._menu.urlPart(),
        url = null;
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
      url = L.Util.getParamString(this._params);
      this._query(url);
    }
  },

  _query: function(url) {
      this.clearLayers();
      this.addLayer(new OsmoseMarker(url, this._editor));
  },

  corrected: function (layer) {
    this._osmoseMarker.corrected(layer);
  },
});
