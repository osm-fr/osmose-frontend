require('leaflet');


L.Control.Location = L.Control.extend({

  options: {
    position: 'topleft',
    menuText: '',
    menuTitle: 'Location',
  },

  initialize(options) {
    L.Control.prototype.initialize.call(this, options);
  },

  onAdd(map) {
    const menuName = 'leaflet-control-location';
    const container = L.DomUtil.create('div', `${menuName} leaflet-bar`);
    this._map = map;
    this._zoomInButton = this._createButton(this.options.menuText, this.options.menuTitle, `${menuName}-in`, container, this._location, this);
    return container;
  },

  _location() {
    this._map.locate({
      setView: true,
    });
  },

  _createButton(html, title, className, container, fn, context) {
    const link = L.DomUtil.create('a', className, container);
    link.style = 'background-image: url(/images/location.png)'; // Firefox
    link.style['background-image'] = 'url(/images/location.png)'; // Chrome
    link.innerHTML = html;
    link.href = '#';
    link.title = title;
    const stop = L.DomEvent.stopPropagation;

    L.DomEvent
      .on(link, 'click', stop)
      .on(link, 'mousedown', stop)
      .on(link, 'dblclick', stop)
      .on(link, 'click', L.DomEvent.preventDefault)
      .on(link, 'click', fn, context)
      .on(link, 'click', this._refocusOnMap, context);

    return link;
  },
});

L.control.location = function (options) {
  return new L.Control.Location(options);
};
