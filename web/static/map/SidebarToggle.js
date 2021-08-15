import 'leaflet';
import 'leaflet-sidebar';
import 'leaflet-sidebar/src/L.Control.Sidebar.css';


const SidebarToggle = L.Control.Sidebar.extend({

  options: {
    autoPan: false,
    localStorageProperty: "sidebar-toggle",
  },

  initialize(placeholder, options) {
    L.Control.Sidebar.prototype.initialize.call(this, placeholder, options);

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
    // Not working well with Vue JS
    // const active_area = document.getElementsByClassName("leaflet-active-area")[0];
    // const style = window.getComputedStyle(active_area);
    // if (style.right === '0px') {
    //   active_area.style.right = '';
    // } else {
    //   active_area.style.right = '0px';
    // }
  },

  show() {
    localStorage.setItem(this.options.localStorageProperty, true);
    L.Control.Sidebar.prototype.show.call(this);
  },
});

export { SidebarToggle as default };
