import SidebarToggle from './SidebarToggle.js';
import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'


const OsmoseDoc = SidebarToggle.extend({

  options: {
    localStorageProperty: "doc.show",
  },

  show(item, classs) {
    SidebarToggle.prototype.show.call(this);
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
