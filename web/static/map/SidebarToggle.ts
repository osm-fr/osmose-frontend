import { Map, ControlOptions } from 'leaflet'
import 'leaflet-sidebar'
import 'leaflet-sidebar/src/L.Control.Sidebar.css'

import ToggleControl from './ToggleControl'

export type SidebarToggleOptions = {
  autoPan: boolean
  localStorageProperty: string
  toggle: any
}

export default class SidebarToggle extends L.Control.Sidebar {
  sidebarToggleOptions: SidebarToggleOptions = {
    autoPan: false,
    localStorageProperty: 'sidebar-toggle',
    toggle: undefined,
  }

  constructor(placeholder, options?: SidebarToggleOptions & ControlOptions) {
    super(placeholder, { position: 'left', ...options })
    Object.assign(this.sidebarToggleOptions, options)
  }

  addTo(map: Map) {
    super.addTo(map)

    map.addControl(new ToggleControl(this, this.sidebarToggleOptions.toggle))

    let show = localStorage.getItem(
      this.sidebarToggleOptions.localStorageProperty
    )
    if (show !== null && JSON.parse(show) === 'false') {
      this.hide()
    } else {
      this.show()
    }
  }

  show(): void {
    localStorage.setItem(this.sidebarToggleOptions.localStorageProperty, 'true')
    super.show()
  }

  hide(): void {
    localStorage.setItem(
      this.sidebarToggleOptions.localStorageProperty,
      'false'
    )
    super.hide()
  }
}
