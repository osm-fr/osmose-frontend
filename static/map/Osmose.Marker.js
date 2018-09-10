require('leaflet');
require('leaflet.vectorgrid/dist/Leaflet.VectorGrid.js');
require('leaflet-responsive-popup');
require('leaflet-responsive-popup/leaflet.responsive.popup.css');
require('leaflet-osm');
require('leaflet-textpath');
require('mustache');
var Cookies = require('js-cookie');

require('./Osmose.Marker.css');


export var OsmoseMarker = L.VectorGrid.Protobuf.extend({

  initialize: function (permalink, params, editor, featuresLayers, options) {
    this._permalink = permalink;
    this._editor = editor;
    this._featuresLayers = featuresLayers;
    this._remote_url_read = remote_url_read;
    L.Util.setOptions(this, options);
    var vectorTileOptions = {
      rendererFactory: L.svg.tile,
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
    L.VectorGrid.Protobuf.prototype.initialize.call(this, this._buildUrl(params), vectorTileOptions);
  },

  _tileReady: function (coords, err, tile) {
    L.VectorGrid.Protobuf.prototype._tileReady.call(this, coords, err, tile);

    // Hack: Overload the tile size an relative position to display part of markers over the edge of the tile.
    var key = this._tileCoordsToKey(coords);
    tile = this._tiles[key];
    if (tile) {
      tile.el.setAttribute('viewBox', '-33 -33 322 322'); // 0-33, 0-33, 256+33, 256+33
      tile.el.style.width = '322px';
      tile.el.style.height = '322px';
      var transform = tile.el.style.transform.match(/translate3d\(([-0-9]+)px, ([-0-9]+)px, 0px\)/);
      var x = parseInt(transform[1]) - 33;
      var y = parseInt(transform[2]) - 33;
      tile.el.style.transform = 'translate3d(' + x + 'px, ' + y + 'px, 0px)'
    }
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
    var click = function (e) {
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
    };
    this.on('click', click);

    map.on('zoomend moveend', L.Util.bind(this._mapChange, this));
    var bindClosePopup = L.Util.bind(this._closePopup, this);
    map.on('zoomstart', bindClosePopup);

    this._permalink.on('update', this._updateOsmoseLayer, this);

    this.once('remove', function() {
      this.off('click', click);
      map.off('zoomstart', bindClosePopup);
      this._permalink.off('update', this._updateOsmoseLayer, this);
    }, this);
  },

  _mapChange: function () {
    var cookies_options = {
      expires: 365,
      path: '/'
    }

    Cookies.set('last_zoom', this._map.getZoom(), cookies_options);
    Cookies.set('last_lat', this._map.getCenter().lat, cookies_options);
    Cookies.set('last_lon', this._map.getCenter().lng, cookies_options);
  },

  _updateOsmoseLayer: function (e) {
    if (this._map.getZoom() >= 6) {
      var newUrl = this._buildUrl(e.params);
      if (this._url != newUrl) {
         this.setUrl(newUrl);
      }
    }
  },

  _buildUrl: function(params) {
    var p = ['level', 'fix', 'tags', 'item', 'class', 'fixable', 'useDevItem', 'source', 'username', 'country'].reduce(function(o, k) {
      if (params[k] !== undefined) {
        o[k] = params[k];
      }
      return o;
    }, {});
    return './issues/{z}/{x}/{y}.mvt' + L.Util.getParamString(p);
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

    var popup = this.popup = L.responsivePopup({
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
            // Get the OSM objects
            self._featuresLayers.clearLayers();
            if (data.elems_id) {
              var shift = -1, palette = ['#ff3333', '#59b300', '#3388ff'], colors = {};
              data.elems.forEach(function(elem) {
                colors[elem.type + elem.id] = palette[(shift += 1) % 3];
                $.ajax({
                  url: elem.type == 'node' ? self._remote_url_read + 'api/0.6/node/' + elem.id:
                    self._remote_url_read + 'api/0.6/' + elem.type + '/' + elem.id + '/full',
                  dataType: 'xml',
                  success: function (xml) {
                    var layer = new L.OSM.DataLayer(xml);
                    layer.setStyle({
                       color: colors[elem.type + elem.id],
                       fillColor: colors[elem.type + elem.id],
                    });
                    layer.setText('  ►  ', {
                       repeat: true,
                       attributes: {
                           fill: colors[elem.type + elem.id]
                       }
                    });
                    self._featuresLayers.addLayer(layer);
                  }
                });
              });
            }
            // Display Popup
            var template = $('#popupTpl').html(),
              content = $(Mustache.render(template, data));
            content.on('click', '.closePopup', function () {
              setTimeout(function () {
                self.corrected(e.layer);
              }, 200);
            });
            content.on('click', '.editor_edit, .editor_fix', function () {
              self._editor.edit(e.layer, this.getAttribute('data-error'), this.getAttribute('data-type'), this.getAttribute('data-id'), this.getAttribute('data-fix'));
              return false;
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

    // Hack, removes the marker directly from the DOM since the style update of icon does not work with SVG renderer.
    //this.setFeatureStyle(layer.properties.issue_id, {});
    layer._path.remove();
  },
});
