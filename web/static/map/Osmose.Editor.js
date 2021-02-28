require('leaflet');

import ExternalVueAppEvent from '../../src/ExternalVueAppEvent.js'


const OsmoseEditor = L.Control.Sidebar.extend({

  options: {
    closeButton: false,
    autoPan: false,
  },

  edit(layer, uuid, fix) {
    this.layer = layer;
    ExternalVueAppEvent.$emit('editor-load', uuid, fix);
  },

  _validate(uuid) {
      this.errors.corrected(this.layer);
  },
});


export { OsmoseEditor as default };
