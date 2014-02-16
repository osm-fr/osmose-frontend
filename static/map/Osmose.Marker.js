OsmoseMarker = L.GeoJSON.extend({

  initialize: function (data, options) {
    L.GeoJSON.prototype.initialize.call(this, data, {
      pointToLayer: this._pointToLayer,
      onEachFeature: this._onEachFeature,
    });
  },

  _pointToLayer: function (featureData, latlng) {
    var marker = L.marker(latlng, {
      icon: L.icon({
        iconUrl: "../images/markers/marker-b-" + featureData.properties.item + ".png",
        iconSize: [17, 33],
        iconAnchor: [8, 33],
        popupAnchor: [0, -33],
      }),
    });

    marker.on('popupopen', function (popup) {
      popup.popup.setContent("<center><img src='../images/throbbler.gif' alt='downloading'></center>");
      popup.popup.update();

      $.ajax({
        url: '../api/0.2/error/' + featureData.properties.error_id,
        dataType: 'json',
        success: function (data) {
          var template = $('#popupTpl').html();
          var content = Mustache.render(template, data);
          popup.popup.setContent(content);
        },
        error: function (jqXHR, textStatus, errorThrown) {
          popup.popup.setContent(textStatus);
        },
      });
    });

    return marker;
  },

  _onEachFeature: function (featureData, layer) {
    layer.bindPopup('').on('mouseover', function (e) {
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
    }).on('popupclose', function (e) {
      layer.click = false;
    });
  },
});
