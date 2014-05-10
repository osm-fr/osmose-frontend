L.SpinMapMixin = {
    spin: function (state) {
        if (!!state) {
            // start spinning !
            if (!this._spinner) {
                this._spinner = true;
                $("div#spinner").html("<img src='../images/throbbler-big.gif' alt='downloading'>");
                $("div#spinner").show()
                this._spinning = 0;
            }
            this._spinning++;
        }
        else {
            this._spinning--;
            if (this._spinning <= 0) {
                // end spinning !
                if (this._spinner) {
                    $("div#spinner").hide()
                    $("div#spinner").html("");
                    this._spinner = null;
                }
            }
        }
    }
};

L.Map.include(L.SpinMapMixin);

L.Map.addInitHook(function () {
    this.on('layeradd', function (e) {
        // If added layer is currently loading, spin !
        if (e.layer.loading) this.spin(true);
        if (typeof e.layer.on != 'function') return;
        e.layer.on('data:loading', function () { this.spin(true); }, this);
        e.layer.on('data:loaded',  function () { this.spin(false); }, this);
    }, this);
    this.on('layerremove', function (e) {
        // Clean-up
        if (e.layer.loading) this.spin(false);
        if (typeof e.layer.on != 'function') return;
        e.layer.off('data:loaded');
        e.layer.off('data:loading');
    }, this);
});
