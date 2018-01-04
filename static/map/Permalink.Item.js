require('leaflet');
require('leaflet-plugins/control/Permalink.js');


L.Control.Permalink.include({

  initialize_item: function () {
    this.on('update', this._set_items, this);
    this.on('add', this._onadd_item, this);
  },

  _onadd_item: function (e) {
    this.options.menu.on('itemchanged', this._update_item, this);
    this._update_item({
      urlPart: this.options.menu.urlPart()
    });
  },

  _update_item: function (e) {
    this._update(e.urlPart);
  },

  _set_items: function (e) {
    var p = e.params;
    if (this.options.menu && (p.item || p.level || p.tags != undefined || p.fixable != undefined)) {
      this.options.menu.setItems(p.item, p.level, p.tags, p.fixable);
    }
  }
});
