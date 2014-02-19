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

  var menu = new OsmoseMenu('menu', {
    position: 'left'
  });
  map.addControl(menu);
  map.addControl(new OsmoseMenuToggle(menu));
  menu.show();

  var osmoseLayer = new OsmoseErrors(menu);
  mapOverlay['Osmose Errors'] = osmoseLayer;
  var layers = L.control.layers(mapBases, mapOverlay);
  map.addControl(layers);

  var permalink = new L.Control.Permalink({
    layers: layers,
    position: 'bottomright',
    menu: menu
  });
  map.addControl(permalink);

  var scale = L.control.scale({
    position: 'bottomright'
  });
  map.addControl(scale);

  var location = L.control.location();
  map.addControl(location);

  var geocode = L.Control.geocoder({
    showResultIcons: true
  });
  geocode.markGeocode = function (result) {
    this._map.fitBounds(result.bbox);
    return this;
  };
  map.addControl(geocode);

  function getUrlVars() {
    var vars = [],
      hash;
    var hashes = window.location.href.slice(window.location.href.indexOf('?') + 1).split('&');
    for (var i = 0; i < hashes.length; i++) {
      hash = hashes[i].split('=');
      vars.push(hash[0]);
      vars[hash[0]] = hash[1];
    }
    return vars;
  }

  if (!getUrlVars()['overlays']) {
    map.addLayer(osmoseLayer);
  }

  $.ajax({
    url: $("#popupTpl").attr("src")
  }).done(function (html) {
    $("#popupTpl").html(html);
  });

  map.on('zoomend', function (e) {
    if (map.getZoom() < 6) {
      $("#need_zoom").show();
      $("#action_links, #tests").hide();
    } else {
      $("#need_zoom").hide();
      $("#action_links, #tests").show();
    }
  });
}
