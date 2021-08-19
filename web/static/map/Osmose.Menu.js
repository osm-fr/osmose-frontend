import './Osmose.Menu.css';
import SidebarToggle from './SidebarToggle.js';


const OsmoseMenu = SidebarToggle.extend({
  options: {
    closeButton: false,
    localStorageProperty: "menu.show",
  },
});

export { OsmoseMenu as default };
