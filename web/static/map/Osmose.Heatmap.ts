import 'leaflet'
import 'leaflet.vectorgrid/dist/Leaflet.VectorGrid'

export default class OsmoseHeatmap extends L.VectorGrid.Protobuf {
  constructor(itemState: any, query: string, options?: LayerOptions) {
    const vectorTileOptions: L.VectorGrid.ProtobufOptions = {
      vectorTileLayerStyles: {
        issues(properties, zoom: number) {
          const color = `#${(properties.color + 0x1000000)
            .toString(16)
            .substr(-6)}`
          return {
            stroke: false,
            fillColor: color,
            fillOpacity: zoom < 13 ? 0.25 + (properties.count / 256) * 0.75 : 1,
            fill: true,
          }
        },
      },
    }
    super('fakeURL', vectorTileOptions)

    this.setURLQuery(query)
  }

  setURLQuery(query: string): void {
    const newUrl = API_URL + `/api/0.3/issues/{z}/{x}/{y}.heat.mvt?${query}`
    if (this._url !== newUrl) {
      this.setUrl(newUrl)
    }
  }
}
