OsmoseMarker = L.GeoJSON.extend({

  _options: {},

  initialize: function (data, editor, options) {
    this._options = options;
    this._editor = editor;
    L.GeoJSON.prototype.initialize.call(this, data, {
      pointToLayer: this._pointToLayer.bind(this),
      onEachFeature: this._onEachFeature.bind(this),
    });
  },

  _pointToLayer: function (featureData, latlng) {
    var marker = L.marker(latlng, {
      icon: L.icon({
        iconUrl: "../images/markers/marker-b-" + featureData.properties.item + ".png",
        iconSize: [17, 33],
        iconAnchor: [8, 33],
        popupAnchor: [0, -41],
      }),
    });

    return marker;
  },

  _onEachFeature: function (featureData, layer) {
    var self = this;
    layer.error_id = featureData.properties.error_id;
    layer.bindPopup(null, {
      maxWidth: 280,
      autoPan: false
    }).on('mouseover', function (e) {
      layer.openPopup();
    }).on('mouseout', function (e) {
      if (!layer.click) {
        layer.closePopup();
      }
    }).off('click').on('click', function (e) {
      if (layer.click) {
        layer.closePopup();
      } else {
        layer.click = true;
        layer.openPopup();
      }
    }).on('add', function (e) {
      if (layer.error_id == self._options.error_id) {
        layer.setPopupContent(self._options.content).openPopup();
      }
    }).on('popupclose', function (e) {
      layer.click = false;
    }).on('popupopen', function (e) {
      if (!e.popup.getContent()) {
        e.popup.setContent("<center><img src='../images/throbbler.gif' alt='downloading'></center>");
        e.popup.update();

        setTimeout(function () {
          if (e.popup._isOpen) {
            // Popup still open, so download content
            $.ajax({
              url: '../api/0.2/error/' + featureData.properties.error_id,
              dataType: 'json',
              success: function (data) {
                var template = $('#popupTpl').html(),
                  content = $(Mustache.render(template, data));
                content.on('click', '.closePopup', function () {
                  setTimeout(function () {
                    layer.closePopup();
                    self.removeLayer(layer);
                  }, 200);
                });
                content.on('click', '.editor_edit, .editor_fix', function () {
                  self._editor.edit(self, layer, this.getAttribute('data-error'), this.getAttribute('data-type'), this.getAttribute('data-id'), this.getAttribute('data-fix'));
                });
                e.popup.setContent(content[0]);
              },
              error: function (jqXHR, textStatus, errorThrown) {
                e.popup.setContent(textStatus);
              },
            });
          } else {
            e.popup.setContent(null);
          }
        }, 100);
      }
    });
  },
});
