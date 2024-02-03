import { Map, Popup, LayerOptions } from 'leaflet'

import 'leaflet-responsive-popup'
import 'leaflet-responsive-popup/leaflet.responsive.popup.css'
import 'leaflet-responsive-popup/leaflet.responsive.popup.rtl.css'
import 'leaflet-textpath'
import OsmDataLayer from './leaflet-osm'
import ExternalVueAppEvent from '../../src/ExternalVueAppEvent'
import IconLimit from '../images/limit.png'
import { Map as MapGl } from 'maplibre-gl'

export default class OsmoseMarker extends L.Layer {
  private _map: Map
  private _mapGl: MapGl
  private _remoteUrlRead: string
  private popup: Popup
  private open_popup?: string // uuid

  constructor(
    mapGl: MapGl,
    itemState,
    remoteUrlRead: string,
    options?: LayerOptions
  ) {
    super(options)

    L.Util.setOptions(this, options)
    this._mapGl = mapGl
    this._itemState = itemState
    this._remoteUrlRead = remoteUrlRead

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
      closeOnClick: false,
    }).setContent(document.getElementById('popupTpl'))
  }

  onAdd(map): void {
    this._map = map

    this._featuresLayers = L.layerGroup()
    map.addLayer(this._featuresLayers)

    map.on("mouseenter", 'markers', () => {
      map.getCanvas().style.cursor = "pointer"
    })

    map.on("mouseleave", 'markers', () => {
      map.getCanvas().style.cursor = ""
    })

    this._mapGl.on('click', 'markers', (e) => {
      if (e.features[0].properties.limit) {
        map.setZoomAround(e.latlng, map.getZoom() + 1)
      } else if (e.features[0].properties.uuid) {
        if (this.highlight === e.features[0].properties.uuid) {
          this._closePopup()
        } else {
          this.highlight = e.features[0].properties.uuid
          this._openPopup(
            e.features[0].properties.uuid,
            [e.lngLat.lat, e.lngLat.lng],
            e.features[0]
          )
        }
      }
    })

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
    this._mapGl.getSource('markers').setTiles([newUrl])
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
      this._featuresLayers.clearLayers()
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
