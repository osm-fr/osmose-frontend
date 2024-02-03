import { ControlOptions } from 'leaflet'

export type ToggleControlOptions = {
  menuText: string
  menuTitle: string
}

export default class ToggleControl extends L.Control {
  toggleControloptions: ToggleControlOptions = {
    menuText: 'x',
    menuTitle: 'toggle',
  }

  private _map: L.Map
  private _toggleFunction
  private _zoomInButton: HTMLElement

  constructor(toggleFunction, options?: ToggleControlOptions & ControlOptions) {
    super({ position: 'topleft', ...options })
    Object.assign(this.toggleControloptions, options)
    this._toggleFunction = toggleFunction
  }

  onAdd(map): HTMLElement {
    const menuName = 'leaflet-control-menu-toggle'
    const container = L.DomUtil.create('div', `${menuName} leaflet-bar`)
    this._map = map
    this._zoomInButton = this._createButton(
      this.toggleControloptions.menuText,
      this.toggleControloptions.menuTitle,
      `${menuName}-in`,
      container,
      this._toggleFunction,
      this
    )
    return container
  }

  _createButton(
    html: string,
    title: string,
    className: string,
    container: HTMLElement,
    fn,
    context
  ): HTMLElement {
    const link = L.DomUtil.create('a', className, container)
    link.innerHTML = html
    link.href = '#'
    link.title = title

    const stop = L.DomEvent.stopPropagation

    L.DomEvent.on(link, 'click', stop)
      .on(link, 'mousedown', stop)
      .on(link, 'dblclick', stop)
      .on(link, 'click', L.DomEvent.preventDefault)
      .on(link, 'click', fn, context)
      .on(link, 'click', this._refocusOnMap, context)

    return link
  }
}
