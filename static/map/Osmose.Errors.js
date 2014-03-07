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
    map.on('moveend', this._updateOsmoseLayer, this);
    this._menu.on('itemchanged', this._updateOsmoseLayer, this);
    this._onMap = true;
    this._updateOsmoseLayer();
  },

  onRemove: function (map) {
    map.off('moveend', this._updateOsmoseLayer, this);
    this._menu.off('itemchanged', this._updateOsmoseLayer, this);
    this._onMap = false;
    this.clearLayers();
  },

  _updateOsmoseLayer: function () {
    if (this._map.getZoom() >= 6) {
      var urlPart = this._menu.urlPart(),
        url = null,
        self = this;
      this._map.spin(true, {
        length: 50,
        radius: 50,
        width: 20,
        direction: -1,
        color: '#fff',
      });
      this._params.item = urlPart.item;
      this._params.level = urlPart.level;
      this._params.tags = urlPart.tags;
      this._params.fixable = urlPart.fixable;
      this._params.bbox = this._map.getBounds().toBBoxString();
      this._params.zoom = this._map.getZoom();
      url = L.Util.getParamString(this._params);
      $.ajax({
        url: 'markers' + url,
        dataType: 'json'
      }).done(function (data) {
        var content = null,
          error_id = null;
        if (self._onMap && self._osmoseMarker) {
          self._osmoseMarker.eachLayer(function (layer) {
            if (layer.getPopup() && layer.getPopup()._isOpen) {
              error_id = layer.error_id;
              content = layer.getPopup().getContent();
            }
          });
        }
        self.clearLayers();
        if (self._onMap) {
          self._osmoseMarker = new OsmoseMarker(data, self._editor, {
            error_id: error_id,
            content: content
          });
          self.addLayer(self._osmoseMarker);
        }
      }).always(function () {
        self._map.spin(false);
      });
    }
  },
});
