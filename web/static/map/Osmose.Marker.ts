import { Map, Popup, LayerOptions } from 'leaflet'

import 'leaflet.vectorgrid/dist/Leaflet.VectorGrid'
import 'leaflet-responsive-popup'
import 'leaflet-responsive-popup/leaflet.responsive.popup.css'
import 'leaflet-responsive-popup/leaflet.responsive.popup.rtl.css'
import 'leaflet-textpath'
import OsmDataLayer from './leaflet-osm'
import ExternalVueAppEvent from '../../src/ExternalVueAppEvent'
import IconLimit from '../images/limit.png'

export default class OsmoseMarker extends L.VectorGrid.Protobuf {
  private _map: Map
  private _remoteUrlRead: string
  private popup: Popup
  private open_popup?: string // uuid

  constructor(
    itemState,
    query: string,
    remoteUrlRead: string,
    options?: LayerOptions
  ) {
    const vectorTileOptions: L.VectorGrid.ProtobufOptions = {
      rendererFactory: L.svg.tile,
      vectorTileLayerStyles: {
        issues(properties, zoom: number) {
          return {
            icon: L.icon({
              iconUrl:
                API_URL + `/images/markers/marker-b-${properties.item}.png`,
              iconSize: [17, 33],
              iconAnchor: [8, 33],
            }),
          }
        },
        limit(properties, zoom: number) {
          properties.limit = true
          return {
            icon: L.icon({
              iconUrl: IconLimit,
              iconSize: L.point(256, 256),
              iconAnchor: L.point(128, 128),
            }),
          }
        },
      },
      interactive: true, // Make sure that this VectorGrid fires mouse/pointer events
      getFeatureId(f) {
        return f.properties.uuid
      },
    }
    super('fakeURL', vectorTileOptions)

    L.Util.setOptions(this, options)
    this._itemState = itemState
    this._remoteUrlRead = remoteUrlRead

    this.setURLQuery(query)

    this.on('add', (e) => {
      if (itemState.issue_uuid) {
        this._openPopup(itemState.issue_uuid, [0, 0], this)
      }
    })

    // this.popup = L.responsivePopup({
    this.popup = L.popup({
      maxWidth: 280,
      minWidth: 240,
      autoPan: false,
    }).setContent(document.getElementById('popupTpl'))
  }

  _tileReady(coords, err, tile): void {
    super._tileReady(coords, err, tile)

    // Hack: Overload the tile size an relative position to display part of markers over the edge of the tile.
    const key = this._tileCoordsToKey(coords)
    tile = this._tiles[key]
    if (tile) {
      tile.el.setAttribute('viewBox', '-33 -33 322 322') // 0-33, 0-33, 256+33, 256+33
      tile.el.style.width = '322px'
      tile.el.style.height = '322px'
      const transform = tile.el.style.transform.match(
        /translate3d\(([-0-9]+)px, ([-0-9]+)px, 0px\)/
      )
      const x = parseInt(transform[1], 10) - 33
      const y = parseInt(transform[2], 10) - 33
      tile.el.style.transform = `translate3d(${x}px, ${y}px, 0px)`
    }
  }

  onAdd(map): void {
    this._map = map

    this._featuresLayers = L.layerGroup()
    map.addLayer(this._featuresLayers)

    L.GridLayer.prototype.onAdd.call(this, map)
    const click = (e) => {
      if (e.layer.properties.limit) {
        map.setZoomAround(e.latlng, map.getZoom() + 1)
      } else if (e.layer.properties.uuid) {
        if (this.highlight === e.layer.properties.uuid) {
          this._closePopup()
        } else {
          this.highlight = e.layer.properties.uuid
          this._openPopup(
            e.layer.properties.uuid,
            [e.latlng.lat, e.latlng.lng],
            e.layer
          )
        }
      }
    }
    this.on('click', click)

    this._map.on('popupclose', (e) => {
      this._itemState.issue_uuid = null
      this.open_popup = undefined
      this._featuresLayers.clearLayers()
    })

    const bindClosePopup = L.Util.bind(this._closePopup, this)
    map.on('zoomstart', bindClosePopup)

    this.once(
      'remove',
      () => {
        this.off('click', click)
        map.off('zoomstart', bindClosePopup)
      },
      this
    )
  }

  setURLQuery(query: string): void {
    const newUrl = API_URL + `/api/0.3/issues/{z}/{x}/{y}.mvt?${query}`
    if (this._url !== newUrl) {
      this.setUrl(newUrl)
    }
  }

  _closePopup(): void {
    this.highlight = undefined
    this.open_popup = undefined
    if (this.popup && this._map) {
      this._map.closePopup(this.popup)
    }
  }

  _openPopup(uuid, initialLatlng, layer): void {
    if (this.open_popup === uuid) {
      return
    }
    this.open_popup = uuid
    this._itemState.issue_uuid = uuid

    ExternalVueAppEvent.$emit('popup-status', 'loading')
    delete this.popup.options.offset
    this.popup.setLatLng(initialLatlng).openOn(this._map)

    setTimeout(() => {
      if (this.popup.isOpen()) {
        // Popup still open, so download content
        ExternalVueAppEvent.$emit('popup-load', uuid)
        this.layer = layer
      } else {
        ExternalVueAppEvent.$emit('popup-status', 'clean')
      }
    }, 100)
  }

  _setPopup(data): void {
    this.popup.options.offset = L.point(0, -24)
    this.popup.setLatLng([data.lat, data.lon])
    data.elems_id = data.elems.map((elem) => elem.type + elem.id).join(',')

    ExternalVueAppEvent.$emit('load-doc', {
      item: data.item,
      classs: data['class'],
    })
    // Get the OSM objects
    if (data.elems_id) {
      let shift = -1
      const palette = ['#ff3333', '#59b300', '#3388ff']
      const colors = {}
      data.elems.forEach((elem) => {
        colors[elem.type + elem.id] = palette[(shift += 1) % 3]
        fetch(
          elem.type === 'node'
            ? `${this._remoteUrlRead}api/0.6/node/${elem.id}`
            : `${this._remoteUrlRead}api/0.6/${elem.type}/${elem.id}/full`
        )
          .then((response) => response.text())
          .then((str) =>
            new window.DOMParser().parseFromString(str, 'text/xml')
          )
          .then((xml) => {
            const layer = new OsmDataLayer(xml)
            layer.setStyle({
              color: colors[elem.type + elem.id],
              fillColor: colors[elem.type + elem.id],
            })
            // Disable leaflet-textpath 1.1.0, not working with Leaflet 1.0.3
            // layer.setText('  ►  ', {
            //   repeat: true,
            //   attributes: {
            //     fill: colors[elem.type + elem.id],
            //   },
            // })
            this._featuresLayers.addLayer(layer)
          })
      })
    }
  }

  _dismissMarker(): void {
    setTimeout(() => {
      this.corrected()
    }, 200)
  }

  _help(item, classs): void {
    ExternalVueAppEvent.$emit('show-doc', { item, classs })
  }

  corrected(): void {
    this._closePopup()

    // Hack, removes the marker directly from the DOM since the style update of icon does not work with SVG renderer.
    // this.setFeatureStyle(layer.properties.uuid, {})
    this.layer._path.remove()
  }
}
