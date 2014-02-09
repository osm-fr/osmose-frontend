function init_map() {
  var layers = [];
  $.each(mapBases, function (name, layer) {
    layers.push(layer);
  });

  var map = L.map('map', {
    center: new L.LatLng(lat, lon),
    zoom: zoom,
    layers: layers[0]
  });

  var osmoseLayer = L.layerGroup([]);
  mapOverlay['Osmose Errors'] = osmoseLayer;
  var layers = L.control.layers(mapBases, mapOverlay);
  map.addControl(layers);

  var scale = L.control.scale({
    position: 'bottomright'
  });
  map.addControl(scale);

  var menu = new OsmoseMenu('menu', {
    position: 'left'
  });
  map.addControl(menu);
  menu.show();

  var permalink = new L.Control.Permalink({
    layers: layers,
    position: 'bottomright',
    menu: menu
  });
  map.addControl(permalink);

  $.ajax({
    url: $("#popupTpl").attr("src")
  }).done(function (html) {
    $("#popupTpl").html(html);
  });

  function updateOsmoseLayer (urlPart) {
    if (map.getZoom() >= 6) {
      var params = {
          item: urlPart.item,
          level: urlPart.level,
          bbox: map.getBounds().toBBoxString(),
          zoom: map.getZoom()
        },
        url = L.Util.getParamString(params);
      $.ajax({
        url: 'markers' + url,
        dataType: 'json'
      }).done(function (data) {
        osmoseLayer.clearLayers();
        osmoseLayer.addLayer(new OsmoseMarker(data));
      });
    }
  }

  map.on('moveend', function (e) {
    updateOsmoseLayer(menu.urlPart());
  }, this);
  menu.on('itemchanged', function (e) {
    updateOsmoseLayer(e.urlPart);
  }, this);

  map.on('zoomend', function (e) {
    if (map.getZoom() < 6) {
      $("div#need_zoom").show();
      $("div#action_links").hide();
      $("div#tests").hide();
    } else {
      $("div#need_zoom").hide();
      $("div#action_links").show();
      if ($("div#menu").data('opened')) {
        $("div#tests").fadeIn();
      }
    }
  });
}
