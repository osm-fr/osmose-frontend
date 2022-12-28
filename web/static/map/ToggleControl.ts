const ToggleControl = L.Control.extend({

  options: {
    position: 'topleft',
  },

  initialize(menu, options) {
    L.Control.prototype.initialize.call(this, options)
    this._menu = menu
  },

  onAdd(map) {
    const menuName = 'leaflet-control-menu-toggle'
    const container = L.DomUtil.create('div', `${menuName} leaflet-bar`)
    this._map = map
    this._zoomInButton = this._createButton(this.options.menuText, this.options.menuTitle, `${menuName}-in`, container, this._menuToggle, this)
    return container
  },

  _menuToggle() {
    this._menu.toggle()
  },

  _createButton(html, title, className, container, fn, context) {
    const link = L.DomUtil.create('a', className, container)
    link.innerHTML = html
    link.href = '#'
    link.title = title

    const stop = L.DomEvent.stopPropagation

    L.DomEvent
      .on(link, 'click', stop)
      .on(link, 'mousedown', stop)
      .on(link, 'dblclick', stop)
      .on(link, 'click', L.DomEvent.preventDefault)
      .on(link, 'click', fn, context)
      .on(link, 'click', this._refocusOnMap, context)

    return link
  },
})

export { ToggleControl as default }
