import 'leaflet'
import 'leaflet-sidebar'
import 'leaflet-sidebar/src/L.Control.Sidebar.css'

import ToggleControl from './ToggleControl'


const SidebarToggle = L.Control.Sidebar.extend({

  options: {
    autoPan: false,
    localStorageProperty: "sidebar-toggle",
  },

  initialize(map, placeholder, options) {
    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options)

    map.addControl(new ToggleControl(this, options.toggle))

    let show = localStorage.getItem(this.options.localStorageProperty)
    if (show !== null && JSON.parse(show) === false) {
      this.hide()
    } else {
      this.show()
    }
  },

  setStyleBorder(border) {
    const active_area = document.getElementsByClassName("leaflet-active-area")[0]
    const style = window.getComputedStyle(active_area)
    active_area.style[this.options.position] = border
  },

  show() {
    localStorage.setItem(this.options.localStorageProperty, true)
    this.setStyleBorder('')
    L.Control.Sidebar.prototype.show.call(this)
  },

  hide() {
    localStorage.setItem(this.options.localStorageProperty, false)
    this.setStyleBorder('0px')
    L.Control.Sidebar.prototype.hide.call(this)
  },
})

export { SidebarToggle as default }
