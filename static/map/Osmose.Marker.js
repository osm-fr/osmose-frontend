OsmoseMarker = L.VectorGrid.Protobuf.extend({

  initialize: function (menu, params, editor, options) {
    this._menu = menu;
    this._params = params;
    this._editor = editor;
    L.Util.setOptions(this, options);
    var vectorTileOptions = {
      rendererFactory: L.canvas.tile,
      vectorTileLayerStyles: {
        issues: function(properties, zoom) {
          return {
            icon: L.icon({
              iconUrl: '../images/markers/marker-b-' + properties.item + '.png',
              iconSize: [17, 33],
              iconAnchor: [8, 33],
            })
          };
        },
        limit: function(properties, zoom) {
          properties.limit = true;
          return {
            icon: L.icon({
              iconUrl: '../images/limit.png',
              iconSize:  L.point(256, 256),
              iconAnchor:  L.point(128, 128),
            })
          };
        }
      },
      interactive: true,  // Make sure that this VectorGrid fires mouse/pointer events
      getFeatureId: function(f) {
        return f.properties.issue_id;
      }
    };
    L.VectorGrid.Protobuf.prototype.initialize.call(this, this._getUrl(), vectorTileOptions);
  },

  onAdd: function(map) {
    this._map = map;
    var self = this;
    L.GridLayer.prototype.onAdd.call(this, map);
/*
    this.on('mouseover', function (e) {
      if (e.layer.properties.issue_id) {
        self._openPopup(e);
      }
    }).on('mouseout', function (e) {
      if (e.layer.properties.issue_id && self.highlight != e.layer.properties.issue_id) {
        self._closePopup();
      }
    });
*/
    this.on('click', function (e) {
      if (e.layer.properties.limit) {
        map.setZoomAround(e.latlng, map.getZoom() + 1);
      } else if (e.layer.properties.issue_id) {
        if (self.highlight == e.layer.properties.issue_id) {
          self._closePopup();
        } else {
          self.highlight = e.layer.properties.issue_id;
          self._openPopup(e);
        }
      }
    });

    var bindClosePopup = L.Util.bind(this._closePopup, this);
    map.on('zoomstart', bindClosePopup);
    this.on('remove', function() {
      map.off('zoomstart', bindClosePopup);
    });

    this._menu.on('itemchanged', this._updateOsmoseLayer, this);
  },

  onRemove: function (map) {
    this._menu.off('itemchanged', this._updateOsmoseLayer, this);
    L.GridLayer.prototype.onRemove.call(this, map);
  },

  _updateOsmoseLayer: function () {
    if (this._map.getZoom() >= 6) {
      this.setUrl(this._getUrl());
    }
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
    return './issues/{z}/{x}/{y}.mvt' + L.Util.getParamString(this._params);
  },

  _closePopup: function () {
    this.highlight = undefined;
    this.open_popup = undefined;
    if(this.popup && this._map) {
      this._map.closePopup(this.popup);
    }
  },

  _openPopup: function (e) {
    if (this.open_popup == e.layer.properties.issue_id) {
      return;
    } else {
      this.open_popup = e.layer.properties.issue_id;
    }

    var popup = this.popup = L.popup({
      maxWidth: 280,
      autoPan: false,
      offset: L.point(0, -8)
    }).setLatLng(e.latlng)
    .setContent("<center><img src='../images/throbbler.gif' alt='downloading'></center>")
    .openOn(this._map);

    var self = this;
    setTimeout(function () {
      if (popup.isOpen) {
        // Popup still open, so download content
        $.ajax({
          url: '../api/0.2/error/' + e.layer.properties.issue_id,
          dataType: 'json',
          success: function (data) {
            var template = $('#popupTpl').html(),
              content = $(Mustache.render(template, data));
            content.on('click', '.closePopup', function () {
              setTimeout(function () {
                self.corrected(e.layer);
              }, 200);
            });
            content.on('click', '.editor_edit, .editor_fix', function () {
              self._editor.edit(e.layer, this.getAttribute('data-error'), this.getAttribute('data-type'), this.getAttribute('data-id'), this.getAttribute('data-fix'));
            });
            popup.setContent(content[0]);
          },
          error: function (jqXHR, textStatus, errorThrown) {
            popup.setContent(textStatus);
          },
        });
      } else {
        popup.setContent(null);
      }
    }, 100);
  },

  corrected: function (layer) {
    this._closePopup();
    this.setFeatureStyle(layer.properties.issue_id, {});
  },
});
