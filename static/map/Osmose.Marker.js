OsmoseMarker = L.VectorGrid.Protobuf.extend({

  initialize: function (url, editor, options) {
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
        limit: {
          icon: L.icon({
            iconUrl: '../images/limit.png',
            iconSize:  L.point(256, 256),
            iconAnchor:  L.point(128, 128),
          })
        }
      },
      interactive: true,  // Make sure that this VectorGrid fires mouse/pointer events
      getFeatureId: function(f) {
        return f.properties.issue_id;
      }
    };
    L.VectorGrid.Protobuf.prototype.initialize.call(this, './issues/{z}/{x}/{y}.mvt' + url, vectorTileOptions);
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
      if (e.layer.properties.issue_id) {
        if (self.highlight == e.layer.properties.issue_id) {
          self._closePopup();
        } else {
          self.highlight = e.layer.properties.issue_id;
          self._openPopup(e);
        }
      }
    });
  },

  _closePopup: function () {
    this.highlight = undefined;
    this.open_popup = undefined;
    if(this.popup) {
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
                self._closePopup();
                e.layer.remove();
              }, 200);
            });
            content.on('click', '.editor_edit, .editor_fix', function () {
              self._editor.edit(layer, this.getAttribute('data-error'), this.getAttribute('data-type'), this.getAttribute('data-id'), this.getAttribute('data-fix'));
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
    if (this.hasLayer(layer)) {
      this.removeLayer(layer);
    } else {
      var self = this;
      this.eachLayer(function (l) {
        if (l.error_id == layer.error_id) {
          self.removeLayer(l);
          return;
        }
      });
    }
  },
});
