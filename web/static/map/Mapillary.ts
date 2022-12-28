import 'leaflet.vectorgrid/dist/Leaflet.VectorGrid'

import { Map } from 'leaflet'

export default class Mapillary extends L.VectorGrid.Protobuf {
  private _map: Map
  private _clientId: string
  private _onClick_bind: () => void

  constructor(clientId: string) {
    super('https://d2munx5tg0hw47.cloudfront.net/tiles/{z}/{x}/{y}.mapbox', {
      getIDForLayerFeature(feature) {
        return feature.properties.id
      },
      zIndex: 2,
      vectorTileLayerStyles: {
        'mapillary-sequences': {
          color: 'rgba(0,255,0,0.8)',
          weight: 3,
        },
      },
    })

    this._clientId = clientId
  }

  onAdd(map): void {
    this._map = map
    super.onAdd(map)
    this._onClick_bind = L.Util.bind(this._onClick, this)
    map.on('click', this._onClick_bind)
  }

  onRemove(map): void {
    super.onRemove(map)
    map.off('click', this._onClick_bind)
  }

  _onClick(e): void {
    // https://www.mapillary.com/developer/api-documentation/#search-images
    this._ajax(
      `https://a.mapillary.com/v3/images?client_id=${this._clientId}&closeto=${e.latlng.lng},${e.latlng.lat}&radius=300&per_page=1`,
      (json) => {
        const im = JSON.parse(json).features[0]

        L.responsivePopup()
          .setLatLng([im.geometry.coordinates[1], im.geometry.coordinates[0]])
          .setContent(
            `<a href='http://www.mapillary.com/map/im/${im.properties.key}/photo' target='_blank'><div style='width: 240px; height: 180px'><img src='https://d1cuyjsrcm0gby.cloudfront.net/${im.properties.key}/thumb-320.jpg' style='max-width: 100%; max-height: 100%; display: block;'/></div>${im.properties.username} - Mapillary - CC BY-SA 4.0</a>`
          )
          .openOn(this._map)
      }
    )
  }

  _ajax(url: string, callback): void {
    const xhr = new XMLHttpRequest()
    xhr.open('GET', url, true)
    xhr.onload = () => {
      if (xhr.status === 200) {
        callback(xhr.response)
      }
    }

    xhr.send()
  }
}
