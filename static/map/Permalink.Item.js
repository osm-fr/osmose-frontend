require('leaflet');
require('leaflet-plugins/control/Permalink.js');


L.Control.Permalink.include({

  initialize_item: function () {
  },

  update_item: function (params) {
    this._update(params);
    this.fire('update', {params: this._params});
  }
});
