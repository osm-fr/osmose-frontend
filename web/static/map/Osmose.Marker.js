require('leaflet');
require('leaflet.vectorgrid/dist/Leaflet.VectorGrid.js');
require('leaflet-responsive-popup');
require('leaflet-responsive-popup/leaflet.responsive.popup.css');
require('leaflet-responsive-popup/leaflet.responsive.popup.rtl.css');
require('leaflet-osm');
require('leaflet-textpath');
const Cookies = require('js-cookie');

import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'
import IconLimit from '../images/limit.png';


const OsmoseMarker = L.VectorGrid.Protobuf.extend({

  initialize(permalink, params, editor, doc, featuresLayers, remoteUrlRead, options) {
    this._permalink = permalink;
    this._editor = editor;
    this._doc = doc;
    this._featuresLayers = featuresLayers;
    this._remoteUrlRead = remoteUrlRead;
    L.Util.setOptions(this, options);
    const vectorTileOptions = {
      rendererFactory: L.svg.tile,
      vectorTileLayerStyles: {
        issues(properties, zoom) {
          return {
            icon: L.icon({
              iconUrl: API_URL + `/images/markers/marker-b-${properties.item}.png`,
              iconSize: [17, 33],
              iconAnchor: [8, 33],
            }),
          };
        },
        limit(properties, zoom) {
          properties.limit = true;
          return {
            icon: L.icon({
              iconUrl: IconLimit,
              iconSize: L.point(256, 256),
              iconAnchor: L.point(128, 128),
            }),
          };
        },
      },
      interactive: true, // Make sure that this VectorGrid fires mouse/pointer events
      getFeatureId(f) {
        return f.properties.uuid;
      },
    };
    this.on('add', (e) => {
      if (params.issue_uuid) {
        this._openPopup(params.issue_uuid, [params.lat, params.lon], this);
      }
    });
    L.VectorGrid.Protobuf.prototype.initialize.call(this, this._buildUrl(params), vectorTileOptions);

    // this.popup = L.responsivePopup({
    this.popup = L.popup({
      maxWidth: 280,
      minWidth: 240,
      autoPan: false,
    }).setContent(document.getElementById('popupTpl'))
  },

  _tileReady(coords, err, tile) {
    L.VectorGrid.Protobuf.prototype._tileReady.call(this, coords, err, tile);

    // Hack: Overload the tile size an relative position to display part of markers over the edge of the tile.
    const key = this._tileCoordsToKey(coords);
    tile = this._tiles[key];
    if (tile) {
      tile.el.setAttribute('viewBox', '-33 -33 322 322'); // 0-33, 0-33, 256+33, 256+33
      tile.el.style.width = '322px';
      tile.el.style.height = '322px';
      const transform = tile.el.style.transform.match(/translate3d\(([-0-9]+)px, ([-0-9]+)px, 0px\)/);
      const x = parseInt(transform[1], 10) - 33;
      const y = parseInt(transform[2], 10) - 33;
      tile.el.style.transform = `translate3d(${x}px, ${y}px, 0px)`;
    }
  },

  onAdd(map) {
    this._map = map;
    L.GridLayer.prototype.onAdd.call(this, map);
    const click = (e) => {
      if (e.layer.properties.limit) {
        map.setZoomAround(e.latlng, map.getZoom() + 1);
      } else if (e.layer.properties.uuid) {
        if (this.highlight === e.layer.properties.uuid) {
          this._closePopup();
        } else {
          this.highlight = e.layer.properties.uuid;
          this._openPopup(e.layer.properties.uuid, [e.latlng.lat, e.latlng.lng], e.layer);
        }
      }
    };
    this.on('click', click);

    this._map.on('popupclose', (e) => {
      this._permalink.update_item({ issue_uuid: null });
      this.open_popup = null;
      this._featuresLayers.clearLayers();
    });


    map.on('zoomend moveend', L.Util.bind(this._mapChange, this));
    const bindClosePopup = L.Util.bind(this._closePopup, this);
    map.on('zoomstart', bindClosePopup);

    this._permalink.on('update', this._updateOsmoseLayer, this);

    this.once('remove', () => {
      this.off('click', click);
      map.off('zoomstart', bindClosePopup);
      this._permalink.off('update', this._updateOsmoseLayer, this);
    }, this);
  },

  _mapChange() {
    const cookiesOptions = {
      expires: 365,
      path: '/',
    };

    Cookies.set('last_zoom', this._map.getZoom(), cookiesOptions);
    Cookies.set('last_lat', this._map.getCenter().lat, cookiesOptions);
    Cookies.set('last_lon', this._map.getCenter().lng, cookiesOptions);
  },

  _updateOsmoseLayer(e) {
    if (this._map.getZoom() >= 7) {
      const newUrl = this._buildUrl(e.params);
      if (this._url !== newUrl) {
        this.setUrl(newUrl);
      }
    }
  },

  _buildUrl(params) {
    const p = ['level', 'fix', 'tags', 'item', 'class', 'fixable', 'useDevItem', 'source', 'username', 'country'].reduce((o, k) => {
      if (params[k] !== undefined) {
        o[k] = params[k];
      }
      return o;
    }, {});
    return API_URL + `/api/0.3/issues/{z}/{x}/{y}.mvt${L.Util.getParamString(p)}`;
  },

  _closePopup() {
    this.highlight = undefined;
    this.open_popup = undefined;
    if (this.popup && this._map) {
      this._map.closePopup(this.popup);
    }
  },

  _openPopup(uuid, initialLatlng, layer) {
    if (this.open_popup === uuid) {
      return;
    }
    this.open_popup = uuid;
    this._permalink.update_item({ issue_uuid: uuid });

    ExternalVueAppEvent.$emit('popup-status', 'loading');
    delete this.popup.options.offset;
    this.popup.setLatLng(initialLatlng).openOn(this._map);

    setTimeout(() => {
      if (this.popup.isOpen) {
        // Popup still open, so download content
        ExternalVueAppEvent.$emit('popup-load', uuid);
        this.layer = layer;
      } else {
        ExternalVueAppEvent.$emit('popup-status', 'clean');
      }
    }, 100);
  },

  _setPopup(data) {
    this.popup.options.offset = L.point(0, -24);
    this.popup.setLatLng([data.lat, data.lon]);
    data.elems_id = data.elems.map(elem => elem.type + elem.id).join(',');

    this._doc.load(data.item, data['class']);
    // Get the OSM objects
    if (data.elems_id) {
      let shift = -1; const palette = ['#ff3333', '#59b300', '#3388ff']; const
        colors = {};
      data.elems.forEach((elem) => {
        colors[elem.type + elem.id] = palette[(shift += 1) % 3];
        $.ajax({
          url: elem.type === 'node' ? `${this._remoteUrlRead}api/0.6/node/${elem.id}`
            : `${this._remoteUrlRead}api/0.6/${elem.type}/${elem.id}/full`,
          dataType: 'xml',
          success: (xml) => {
            const layer = new L.OSM.DataLayer(xml);
            layer.setStyle({
              color: colors[elem.type + elem.id],
              fillColor: colors[elem.type + elem.id],
            });
            layer.setText('  ►  ', {
              repeat: true,
              attributes: {
                fill: colors[elem.type + elem.id],
              },
            });
            this._featuresLayers.addLayer(layer);
          },
        });
      });
    }
  },

  _dismissMarker() {
    setTimeout(() => {
      this.corrected(this.layer);
    }, 200);
  },

  _help(item, classs) {
    this._doc.show(item, classs);
  },

  _edit(uuid, fix) {
    this._editor.edit(this.layer, uuid, fix);
  },

  corrected(layer) {
    this._closePopup();

    // Hack, removes the marker directly from the DOM since the style update of icon does not work with SVG renderer.
    // this.setFeatureStyle(layer.properties.uuid, {});
    layer._path.remove();
  },
});


export { OsmoseMarker as default };
