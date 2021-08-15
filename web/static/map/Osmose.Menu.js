import 'leaflet';
import 'leaflet-sidebar';
import 'leaflet-sidebar/src/L.Control.Sidebar.css';
import * as Cookies from 'js-cookie';

import './Osmose.Menu.css';
import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'


export const OsmoseMenu = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  initialize(placeholder, permalink, params, options) {
    this._permalink = permalink;
    this._params = params;

    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);
  },

  init() {
    document.getElementById('togglemenu').onclick = () => {
      this.toggle();
      return false;
    };

    this._setParams({ params: this._params });
    this._permalink.on('update', this._setParams, this);
  },

  // Menu
  toggle() {
    L.Control.Sidebar.prototype.toggle.call(this);
    // Not working well with Vue JS
    // const active_area = document.getElementsByClassName("leaflet-active-area")[0];
    // const style = window.getComputedStyle(active_area);
    // if (style.left === '0px') {
    //   active_area.style.left = '';
    // } else {
    //   active_area.style.left = '0px';
    // }
  },

  _itemChanged(item_mask, level, fixable, tags) {
    const cookiesOptions = {
      expires: 365,
      path: '/',
    };

    if (!level) {
      Cookies.remove('last_level', cookiesOptions);
    } else {
      Cookies.set('last_level', level, cookiesOptions);
    }

    if (!item_mask) {
      Cookies.set('last_item', '', cookiesOptions);
    } else {
      Cookies.set('last_item', item_mask, cookiesOptions);
    }

    if (!tags) {
      Cookies.remove('last_tags', cookiesOptions);
    } else {
      Cookies.set('last_tags', tags, cookiesOptions);
    }

    if (!fixable) {
      Cookies.remove('last_fixable', cookiesOptions);
    } else {
      Cookies.set('last_fixable', fixable, cookiesOptions);
    }

    this._permalink.update_item({
      item: item_mask,
      level,
      tags,
      fixable,
    });
  },

  _setParams(e) {
    const { params } = e;
    ExternalVueAppEvent.$emit("item-params-changed", params);
  },
});


export const OsmoseMenuToggle = L.Control.extend({

  options: {
    position: 'topleft',
    menuText: '☰',
    menuTitle: 'Menu',
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
