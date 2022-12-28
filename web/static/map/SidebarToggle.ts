import { Map, ControlOptions } from 'leaflet'
import 'leaflet-sidebar'
import 'leaflet-sidebar/src/L.Control.Sidebar.css'

import ToggleControl from './ToggleControl'

export type SidebarToggleOptions = {
  autoPan: boolean
  localStorageProperty: string
  position: string
  toggle: any
}

export default class SidebarToggle extends L.Control.Sidebar {
  options: SidebarToggleOptions = {
    autoPan: false,
    localStorageProperty: 'sidebar-toggle',
    position: 'left',
    toggle: undefined,
  }

  constructor(placeholder, options?: SidebarToggleOptions & ControlOptions) {
    super(placeholder, options)
    L.setOptions(this, options)
  }

  addTo(map: Map) {
    super.addTo(map)

    map.addControl(new ToggleControl(this, this.options.toggle))

    let show = localStorage.getItem(this.options.localStorageProperty)
    if (show !== null && JSON.parse(show) === 'false') {
      this.hide()
    } else {
      this.show()
    }
  }

  setStyleBorder(border): void {
    const active_area = document.getElementsByClassName(
      'leaflet-active-area'
    )[0] as HTMLElement
    const style = window.getComputedStyle(active_area)
    active_area.style[this.options.position] = border
  }

  show(): void {
    localStorage.setItem(this.options.localStorageProperty, 'true')
    this.setStyleBorder('')
    super.show()
  }

  hide(): void {
    localStorage.setItem(this.options.localStorageProperty, 'false')
    this.setStyleBorder('0px')
    super.hide()
  }
}
