function init_map() {
  var urlVars = getUrlVars();

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

  var editor = new OsmoseEditor('editor', {
    position: 'right'
  });
  map.addControl(editor);

  mapOverlay['Osmose Errors Heatmap'] = new OsmoseHeatmap(menu);
  var osmoseLayer = new OsmoseErrors(menu, urlVars, editor);
  mapOverlay['Osmose Errors'] = osmoseLayer;
  editor.errors = osmoseLayer;

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

  if (!urlVars.overlays) {
    map.addLayer(osmoseLayer);
  }

  $.ajax({
    url: $("#popupTpl").attr("src")
  }).done(function (html) {
    $("#popupTpl").html(html);
  });

  $.ajax({
    url: $("#editorTpl").attr("src")
  }).done(function (html) {
    $("#editorTpl").html(html);
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
