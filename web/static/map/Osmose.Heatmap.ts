import 'leaflet'
import { Map as MapGl } from 'maplibre-gl'

export default class OsmoseHeatmap extends L.Layer {
  private _mapGl: MapGl

  constructor(
    mapGl: MapGl,
    options?: LayerOptions
  ) {
    super(options)

    L.Util.setOptions(this, options)
    this._mapGl = mapGl
  }

  setURLQuery(query: string): void {
    const newUrl = API_URL + `/api/0.3/issues/{z}/{x}/{y}.heat.mvt?${query}`
    this._mapGl.getSource('heatmap').setTiles([newUrl])
  }

  onAdd(map): void {
  }
}
