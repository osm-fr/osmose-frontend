import { IControl, Map } from 'maplibre-gl'

export type ToggleControlOptions = {
  menuText: string
  menuTitle: string
}

export default class ToggleControl implements IControl {
  toggleControloptions: ToggleControlOptions = {
    menuText: 'x',
    menuTitle: 'toggle',
  }

  private _toggleFunction

  constructor(toggleFunction, options?: ToggleControlOptions) {
    this._toggleFunction = toggleFunction
    Object.assign(this.toggleControloptions, options)
  }

  onAdd(map: Map): HTMLElement {
    const controlContainer = document.createElement('div')
    controlContainer.className = 'maplibregl-ctrl maplibregl-ctrl-group'
    controlContainer.innerHTML = `
      <button class='maplibregl-ctrl-toggle' title='${this.toggleControloptions.menuTitle}'>
        <span class='maplibregl-ctrl-icon' aria-hidden='true' style="width: 30px; height: 30px; line-height: 30px;">${this.toggleControloptions.menuText}</span>
      </button>
    `
    const button = controlContainer.childNodes[1]
    button.addEventListener('click', this._toggleFunction)

    return controlContainer
  }

  onRemove(map: Map): void {}
}
