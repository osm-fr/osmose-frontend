import 'leaflet';
import 'leaflet-sidebar';
import 'leaflet-sidebar/src/L.Control.Sidebar.css';

import ToggleControl from './ToggleControl';


const SidebarToggle = L.Control.Sidebar.extend({

  options: {
    autoPan: false,
    localStorageProperty: "sidebar-toggle",
  },

  initialize(map, placeholder, options) {
    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);

    map.addControl(new ToggleControl(this, options.toggle));

    let show = localStorage.getItem(this.options.localStorageProperty);
    if (show !== null && JSON.parse(show) === false) {
      L.Control.Sidebar.prototype.hide.call(this);
    } else {
      this.show();
    }
  },

  toggle() {
    localStorage.setItem(this.options.localStorageProperty, !JSON.parse(localStorage.getItem(this.options.localStorageProperty)));
    L.Control.Sidebar.prototype.toggle.call(this);

    const active_area = document.getElementsByClassName("leaflet-active-area")[0];
    const style = window.getComputedStyle(active_area);
    if (style[this.options.position] === '0px') {
      active_area.style[this.options.position] = '';
    } else {
      active_area.style[this.options.position] = '0px';
    }
  },

  show() {
    localStorage.setItem(this.options.localStorageProperty, true);
    L.Control.Sidebar.prototype.show.call(this);
  },
});

export { SidebarToggle as default };
