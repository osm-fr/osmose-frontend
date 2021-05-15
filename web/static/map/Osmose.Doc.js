import 'leaflet';
import 'leaflet-sidebar';
import 'leaflet-sidebar/src/L.Control.Sidebar.css';

import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'


export const OsmoseDoc = L.Control.Sidebar.extend({

  options: {
//    closeButton: false,
    autoPan: false,
  },

  initialize(placeholder, options) {
    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);

    let show = localStorage.getItem('doc.show');
    if (show !== null && JSON.parse(show) === false) {
      L.Control.Sidebar.prototype.hide.call(this);
    } else {
      this.show();
    }
  },

  toggle() {
    localStorage.setItem('doc.show', !JSON.parse(localStorage.getItem('doc.show')));
    L.Control.Sidebar.prototype.toggle.call(this);
    // Not working well with Vue JS
    // const active_area = document.getElementsByClassName("leaflet-active-area")[0];
    // const style = window.getComputedStyle(active_area);
    // if (style.right === '0px') {
    //   active_area.style.right = '';
    // } else {
    //   active_area.style.right = '0px';
    // }
  },

  show(item, classs) {
    localStorage.setItem('doc.show', true);
    L.Control.Sidebar.prototype.show.call(this);
    if (item !== undefined) {
      this._load(item, classs);
    }
  },

  load(item, classs) {
    if (this.isVisible()) {
      this._load(item, classs);
    }
  },

  _load(item, classs) {
    ExternalVueAppEvent.$emit("load-doc", item, classs);
  },
});

export const OsmoseDocToggle = L.Control.extend({

  options: {
    position: 'topright',
    menuText: 'ℹ',
    menuTitle: 'Doc',
  },

  initialize(menu, options) {
    L.Control.prototype.initialize.call(this, options);
    this._menu = menu;
  },


  onAdd(map) {
    const menuName = 'leaflet-control-menu-toggle';
    const container = L.DomUtil.create('div', `${menuName} leaflet-bar`);
    this._map = map;
    this._zoomInButton = this._createButton(this.options.menuText, this.options.menuTitle, `${menuName}-in`, container, this._menuToggle, this);
    return container;
  },

  _menuToggle() {
    this._menu.toggle();
  },

  _createButton(html, title, className, container, fn, context) {
    const link = L.DomUtil.create('a', className, container);
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
