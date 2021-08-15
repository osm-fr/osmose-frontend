import 'leaflet';
import 'leaflet-sidebar';
import 'leaflet-sidebar/src/L.Control.Sidebar.css';

import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'


const OsmoseDoc = L.Control.Sidebar.extend({

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

export { OsmoseDoc as default };
