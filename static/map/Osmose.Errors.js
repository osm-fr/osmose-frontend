OsmoseErrors = L.LayerGroup.extend({

  _menu: null,

  _onMap: false,

  _osmoseMarker: null,

  initialize: function (menu) {
    L.LayerGroup.prototype.initialize.call(this);
    this._menu = menu;
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
        params = {
          item: urlPart.item,
          level: urlPart.level,
          bbox: this._map.getBounds().toBBoxString(),
          zoom: this._map.getZoom()
        },
        url = L.Util.getParamString(params),
        self = this;
      $.ajax({
        url: 'markers' + url,
        dataType: 'json'
      }).done(function (data) {
        var content = null,
         error_id = null;
        if (self._onMap && self._osmoseMarker) {
          self._osmoseMarker.eachLayer (function (layer) {
            if (layer.getPopup() && layer.getPopup()._isOpen) {
              error_id = layer.error_id;
              content = layer.getPopup().getContent();
            }
          });
        }
        self.clearLayers();
        if (self._onMap) {
          self._osmoseMarker = new OsmoseMarker(data, {
            error_id: error_id,
            content: content
          });
          self.addLayer(self._osmoseMarker);
        }
      });
    }
  },
});
