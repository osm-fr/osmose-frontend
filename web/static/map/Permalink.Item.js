import 'leaflet';
import 'leaflet-plugins/control/Permalink.js';


L.Control.Permalink.include({

  initialize_item() {
  },

  update_item(params) {
    this._update(params);
    this.fire('update', { params: this._params });
  },
});
