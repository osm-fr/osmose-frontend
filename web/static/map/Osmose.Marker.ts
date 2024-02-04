import { Map, Popup } from 'maplibre-gl'

import osm2geojson from './osm2geojson'
import ExternalVueAppEvent from '../../src/ExternalVueAppEvent'

export default class OsmoseMarker {
  private _map: Map
  private _remoteUrlRead: string
  private popup: Popup
  private open_popup?: string // uuid

  constructor(map: Map, itemState, remoteUrlRead: string) {
    this._map = map
    this._itemState = itemState
    this._remoteUrlRead = remoteUrlRead

    this.popup = new Popup({ closeOnClick: false })
      .setMaxWidth('280')
      .setOffset([0, -24])
      .setDOMContent(document.getElementById('popupTpl'))

    if (this._itemState.issue_uuid) {
      this._openPopup(this._itemState.issue_uuid, [0, 0], this)
    }

    map.on('mouseenter', 'markers', () => {
      map.getCanvas().style.cursor = 'pointer'
    })

    map.on('mouseleave', 'markers', () => {
      map.getCanvas().style.cursor = ''
    })

    map.on('click', 'markers', (e) => {
      e.preventDefault()
      if (e.features[0].properties.uuid) {
        if (this.highlight === e.features[0].properties.uuid) {
          this._closePopup()
        } else {
          this.highlight = e.features[0].properties.uuid
          this._openPopup(
            e.features[0].properties.uuid,
            e.features[0].geometry.coordinates.slice(),
            e.features[0]
          )
        }
      }
    })

    map.on('click', (e) => {
      if (e.defaultPrevented === false) {
        this._closePopup()
      }
    })

    this.popup.on('close', (e) => {
      this._itemState.issue_uuid = null
      this.open_popup = undefined
      this.clearOsmLayer()
    })

    map.on('zoomstart', () => {
      this.popup.remove()
    })
  }

  setURLQuery(query: string): void {
    const newUrl = API_URL + `/api/0.3/issues/{z}/{x}/{y}.mvt?${query}`
    this._map.getSource('markers').setTiles([newUrl])
  }

  _closePopup(): void {
    this.highlight = undefined
    this.open_popup = undefined
    if (this.popup && this._map) {
      this.popup.remove()
    }
  }

  _openPopup(uuid, lngLat, layer): void {
    if (this.open_popup === uuid) {
      return
    }
    this.open_popup = uuid
    this._itemState.issue_uuid = uuid

    ExternalVueAppEvent.$emit('popup-status', 'loading')
    this.popup.setLngLat(lngLat).addTo(this._map)

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
    data.elems_id = data.elems.map((elem) => elem.type + elem.id).join(',')

    ExternalVueAppEvent.$emit('load-doc', {
      item: data.item,
      classs: data['class'],
    })
    // Get the OSM objects
    if (data.elems_id) {
      let shift = -1
      this.clearOsmLayer()
      data.elems.forEach((elem) => {
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
            const geojson = osm2geojson(xml)
            this._map.getSource('osm').setData(geojson)
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
  }

  clearOsmLayer(): void {
    this._map.getSource('osm').setData({
      type: 'FeatureCollection',
      features: [],
    })
  }
}
