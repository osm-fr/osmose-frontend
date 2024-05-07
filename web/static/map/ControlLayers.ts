import { IControl, Map, SourceSpecification, Style } from 'maplibre-gl'

export default class ControlLayers implements IControl {
  private _map: Map
  private _baseLayers: Record<string, SourceSpecification>
  private _overlays: Record<string, string>

  constructor(
    baseLayers: Record<string, SourceSpecification>,
    overlays: Record<string, string>
  ) {
    this._baseLayers = baseLayers
    this._overlays = overlays
  }

  onAdd(map) {
    this._map = map

    const controlContainer = document.createElement('div')
    controlContainer.className =
      'maplibregl-ctrl maplibregl-ctrl-group maplibregl-ctrl-control-layers'

    const button = `
    <button class='maplibregl-ctrl-toggle'
      <span>▤</span>
    </button>
    `
    controlContainer.innerHTML = button

    this._map.once('load', () => {
      const backgroundTile = map.getSource('background').tiles[0]
      let selectors = Object.entries(this._baseLayers)
        .map(([layer, spec]) => {
          const checked = backgroundTile === spec.tiles[0]
          return `
        <div>
          <input type="radio" id="maplibregl-ctrl-layers-selector-${layer}" data-layer="${layer}" class="maplibregl-ctrl-layers-selector" name="maplibregl-ctrl-layers-selector-base-layers"${
            checked ? ' checked="checked"' : ''
          }/>
          <label for="maplibregl-ctrl-layers-selector-${layer}">${layer}</label>
        </div>
      `
        })
        .join('\n')
      selectors += '<hr/>'
      selectors += Object.entries(this._overlays)
        .map(([layer, name]) => {
          const checked = layer == 'markers'
          return `
        <div>
          <input type="checkbox" id="maplibregl-ctrl-layers-selector-${layer}" data-layer="${layer}" class="maplibregl-ctrl-layers-selector"${
            checked ? ' checked="checked"' : ''
          }/>
          <label for="maplibregl-ctrl-layers-selector-${layer}">${name}</label>
        </div>
      `
        })
        .join('\n')
      selectors = `<form style="display: none; margin: 10px;">${selectors}</form>`
      selectors = `
        ${button}
        ${selectors}
      `
      controlContainer.innerHTML = selectors
      const form = controlContainer.childNodes[3] as HTMLFormElement
      const inputs = Array.from(form.querySelectorAll('input'))
      inputs.forEach((input: HTMLInputElement) => {
        input.addEventListener('change', () => this._onInputChange(inputs))
      })

      this._onInputChange(inputs)
    })

    return controlContainer
  }

  onRemove(map: Map): void {}

  _onInputChange(inputs: HTMLInputElement[]) {
    // Background
    inputs
      .filter(
        (input) => input.checked && input.dataset.layer! in this._baseLayers
      )
      .forEach((input) => {
        const layer = this._baseLayers[input.dataset.layer!]
        const source = this._map.getSource('background')
        if (source.tiles !== layer.tiles) {
          source.tileSize = layer.tileSize
          source.attribution = layer.attribution
          source.minzoom = layer.minzoom
          source.maxzoom = layer.maxzoom
          source.setTiles(layer.tiles)
          this.layerReadd('background', 'visible')
        }
      })

    // Overlays
    const checkedOverlays = Object.fromEntries(
      inputs
        .filter((input) => input.dataset.layer! in this._overlays)
        .map((input) => [input.dataset.layer, input.checked])
    )
    this._map.getLayersOrder().forEach((layerId) => {
      const layer = this._map.getLayer(layerId)
      if (layer?.source && layer.source in checkedOverlays) {
        this.layerReadd(
          layerId,
          checkedOverlays[layer.source] ? 'visible' : 'none'
        )
      }
    })
  }

  layerReadd(layerId, visibility) {
    const oldLayers = this._map.getStyle().layers
    const layerIndex = oldLayers.findIndex((l) => l.id === layerId)
    const layerDef = oldLayers[layerIndex]
    if (layerDef.layout) {
      layerDef.layout.visibility = visibility
    } else {
      layerDef.layout = { visibility: visibility }
    }
    const before = oldLayers[layerIndex + 1] && oldLayers[layerIndex + 1].id
    this._map.removeLayer(layerId)
    this._map.addLayer(layerDef, before)
  }
}
