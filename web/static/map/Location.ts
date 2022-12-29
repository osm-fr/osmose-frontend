import { Map, ControlOptions } from 'leaflet'

import IconLocation from '../images/location.png'

export type LocationOptions = {
  menuText: string
  menuTitle: string
}

export default class Location extends L.Control {
  locationOptions: LocationOptions = {
    menuText: '',
    menuTitle: 'Location',
  }

  private _map: Map

  constructor(options: LocationOptions & ControlOptions) {
    super({ position: 'topleft', ...options })
    Object.assign(this.locationOptions, options)
  }

  onAdd(map: Map): HTMLElement {
    const menuName = 'leaflet-control-location'
    const container = L.DomUtil.create('div', `${menuName} leaflet-bar`)
    this._map = map
    this._zoomInButton = this._createButton(
      this.locationOptions.menuText,
      this.locationOptions.menuTitle,
      `${menuName}-in`,
      container,
      this._location,
      this
    )
    return container
  }

  _location(): void {
    this._map.locate({
      setView: true,
    })
  }

  _createButton(
    html: string,
    title: string,
    className: string,
    container: string,
    fn,
    context
  ): HTMLElement {
    const link = L.DomUtil.create('a', className, container)
    link.style = `background-image: url(${IconLocation})` // Firefox
    link.style[`background-image'] = 'url(${IconLocation})`] // Chrome
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

L.control.location = (options: LocationOptions) => new Location(options)
