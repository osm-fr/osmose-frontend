OsmoseErrors = L.LayerGroup.extend({

  menu: null,

  initialize: function (menu) {
    L.LayerGroup.prototype.initialize.call(this);
    this._menu = menu;
    this._updateOsmoseLayerBind = this._updateOsmoseLayer.bind(this);
  },

  onAdd: function (map) {
    this._map = map;
    map.on('moveend', this._updateOsmoseLayerBind, this);
    this._menu.on('itemchanged', this._updateOsmoseLayerBind, this);
    this._updateOsmoseLayer();
  },

  onRemove: function (map) {
    map.off('moveend', this._updateOsmoseLayerBind, this);
    this._menu.off('itemchanged', this._updateOsmoseLayerBind, this);
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
        self.clearLayers();
        self.addLayer(new OsmoseMarker(data));
      });
    }
  },
});
