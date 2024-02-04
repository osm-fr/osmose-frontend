import { Map } from 'maplibre-gl'

export default class OsmoseHeatmap {
  private _map: Map

  constructor(map: Map) {
    this._map = map
  }

  setURLQuery(query: string): void {
    const newUrl = API_URL + `/api/0.3/issues/{z}/{x}/{y}.heat.mvt?${query}`
    this._map.getSource('heatmap').setTiles([newUrl])
  }
}
