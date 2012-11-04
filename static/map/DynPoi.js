/* Copyright (c) 2006-2008 MetaCarta, Inc., published under a modified BSD license.
 * See http://svn.openlayers.org/trunk/openlayers/repository-license.txt
 * for the full text of the license.
 *
 * modified by Harald Kleiner, 2009-02-05
 * expanded text format with new columns specific to keepright
 * created special content inside the bubbles
 *
 * modified by Etienne Chove, 2009-06-12
 * merge some files and simplify functions
 *
 * modified by Nicolas Bouthors, 2012-06-23
 * permalink update
 */
OpenLayers.Format.DynPoiFormat = OpenLayers.Class(OpenLayers.Format, {

    initialize: function (options) {
        OpenLayers.Format.prototype.initialize.apply(this, [options]);
    },

    read: function (text) {
        var lines = text.split('\n');
        var columns;
        var features = [];
        for (var lcv = 0; lcv < (lines.length - 1); lcv++) {
            var currLine = lines[lcv].replace(/^\s*/, '').replace(/\s*$/, '');

            if (!columns) {
                //First line is columns
                columns = currLine.split('\t');
            } else {
                var vals = currLine.split('\t');
                var geometry = new OpenLayers.Geometry.Point(0, 0);
                var attributes = {};
                var style = {};
                var icon, iconSize, iconOffset, overflow;
                var set = false;
                for (var valIndex = 0; valIndex < vals.length; valIndex++) {
                    if (vals[valIndex]) {
                        if (columns[valIndex] == 'lat') {
                            geometry.y = parseFloat(vals[valIndex]);
                            attributes['lat'] = geometry.y;
                            set = true;
                        } else if (columns[valIndex] == 'lon') {
                            geometry.x = parseFloat(vals[valIndex]);
                            attributes['lon'] = geometry.x;
                            set = true;
                        } else if (columns[valIndex] == 'item') {
                            style['item'] = vals[valIndex];
                        } else if (columns[valIndex] == 'marker_id') {
                            attributes['marker_id'] = vals[valIndex];
                        }
                    }
                }
                if (set) {
                    if (this.internalProjection && this.externalProjection) {
                        geometry.transform(this.externalProjection, this.internalProjection);
                    }
                    var feature = new OpenLayers.Feature.Vector(geometry, attributes, style);
                    features.push(feature);
                }
            }
        }
        return features;
    },

    CLASS_NAME: "OpenLayers.Format.DynPoiFormat"
});

function generateBubble(marker_id, text) {
    var s;
    s  = "<div id=\"popup-" + marker_id + "\">";
    s += "<div class=\"bulle_msg\">";
    s += "<div class=\"closebubble\">";
    s += "<div><a href=\"#\" onclick=\"closeBubble('" + marker_id + "');return false;\"><b>&nbsp;X&nbsp;</b></a></div>"
    s += "</div>"
    s += "<div class=\"bulle_err\">";
    s += text;
    s += "</div>";
    s += "<div class=\"bulle_elem\">"
    s += text;
    s += "</div>";
    s += "</div>";
    s += "<div class=\"bulle_verif\">"
    s += text;
    s += "</div>";
    s += "<div class=\"bulle_maj\">"
    s += text;
    s += "</div>";
    s += "</div>";
    return s
}


function closeBubble(marker_id) {
    var b = $("div#popup-" + marker_id).parent().parent().parent();
    b.hide();
}

function fixBubbleHeigth(id) {
  var height = $("div#popup-" + id + " .bulle_verif").height() + $("div#popup-" + id + " .bulle_maj").height();
  $("div#popup-" + id + " .bulle_msg").height($("div#popup-" + id).parent().height() - height);
}

OpenLayers.Layer.DynPoi = OpenLayers.Class(OpenLayers.Layer.Markers, {

    location: null,
    features: null,
    formatOptions: null,
    selectedFeature: null,
    downloaded: false,
    activePopup: false,
    clicked: false,
    marker_ids: {},

    initialize: function (name, options) {
        OpenLayers.Layer.Markers.prototype.initialize.apply(this, arguments);
        this.features = new Array();
    },

    destroy: function () {
        OpenLayers.Layer.Markers.prototype.destroy.apply(this, arguments);
        this.clearFeatures();
        this.features = null;
    },

    loadText: function (params) {
        if (this.location != null) {

            var onFail = function (e) {
                this.events.triggerEvent("loadend");
            };

            this.events.triggerEvent("loadstart");
            OpenLayers.Request.GET({
                url: this.location + params,
                success: this.parseData,
                failure: onFail,
                scope: this
            });

            this.loaded = true;
        }
    },

    moveTo: function (bounds, zoomChanged, minor) {
        OpenLayers.Layer.Markers.prototype.moveTo.apply(this, arguments);
        if (this.visibility && !this.loaded) {
            updateURL();
        }
    },

    parseData: function (ajaxRequest) {

        function create_markerbubble_feature(thisObject, feature) {
            var data = {};
            var location;
            var iconSize, iconOffset;

            location = new OpenLayers.LonLat(feature.geometry.x, feature.geometry.y);
            iconSize = new OpenLayers.Size(17,33);
            iconOffset = new OpenLayers.Pixel(-8,-33);
            data.icon = new OpenLayers.Icon("../images/markers/marker-b-"+feature.style.item+".png", iconSize, iconOffset);

            data['overflow'] = feature.attributes.overflow || "auto";
            data.marker_id = feature.attributes.marker_id;

            var markerFeature = new OpenLayers.Feature(thisObject, location, data);
            markerFeature.popupClass = OpenLayers.Popup.FramedCloud;

            thisObject.features.push(markerFeature);
            var marker = markerFeature.createMarker();
            if (feature.attributes.marker_id != null) {
                marker.events.register("mousedown", markerFeature, thisObject.onClickHandler);
                marker.events.register("mouseover", markerFeature, thisObject.onHOverHandler);
                marker.events.register("mouseout", markerFeature, thisObject.onOutHandler);
            }
            thisObject.addMarker(marker);
            return markerFeature.id;
        }

        var text = ajaxRequest.responseText;

        var options = {};

        OpenLayers.Util.extend(options, this.formatOptions);

        if (this.map && !this.projection.equals(this.map.getProjectionObject())) {
            options.externalProjection = this.projection;
            options.internalProjection = this.map.getProjectionObject();
        }

        var parser = new OpenLayers.Format.DynPoiFormat(options);
        var features = parser.read(text);
        var newfeatures = {};
        var marker_id;
        for (var i = 0, len = features.length; i < len; i++) {
            marker_id = features[i].attributes.marker_id;
            if (marker_id != undefined && marker_id != null) {
                if (!this.marker_ids[marker_id]) {
                    this.marker_ids[marker_id] = create_markerbubble_feature(this, features[i]);
                }
                newfeatures[marker_id] = true;
            }
        }

        // now remove features not needed any more
        var feature_id = null;
        for (var i in this.marker_ids) {
            if (!newfeatures[i]) {
                //console.log("dropping marker id " + i + " " + this.marker_ids[i]);
                feature_id = this.marker_ids[i];
                var featureToDestroy = null;
                var j = 0;
                var len = this.features.length;
                while (j < len && featureToDestroy == null) {
                    if (this.features[j].id == feature_id) {
                        featureToDestroy = this.features[j];
                    }
                    j++;
                }
                if (featureToDestroy != null) {
                    OpenLayers.Util.removeItem(this.features, featureToDestroy);
                    // the marker associated to the feature has to be removed from map.markers manually
                    var markerToDestroy = null;
                    var k = 0;
                    var len = this.markers.length;
                    while (k < len && markerToDestroy == null) {
                        if (this.markers[k].events.element.id == featureToDestroy.marker.events.element.id) {
                            markerToDestroy = this.markers[k];
                        }
                        k++;
                    }
                    OpenLayers.Util.removeItem(this.markers, markerToDestroy);
                    featureToDestroy.destroy();
                    featureToDestroy = null;
                }
                delete this.marker_ids[i];
            }
        }

        this.events.triggerEvent("loadend");

    },

    onClickHandler: function (evt) {
        if (this.clicked && this.activePopup) {
            this.popup.hide();
            this.clicked = false;
        } else if ((this.clicked && !this.activePopup) || !this.clicked) {
            if (this.activePopup) {
                this.popup.hide();
            }
            if (this.popup == null) {
                this.popup = this.createPopup();
                this.popup.autoSize = true;
                this.popup.panMapIfOutOfView = false; //document.myform.autopan.checked;
                this.popup.minSize = new OpenLayers.Size(180, 30);
                this.popup.maxSize = new OpenLayers.Size(280, 300);
                map.addPopup(this.popup);
            } else {
                this.popup.toggle();
            }
            this.activePopup = true;
            this.clicked = true;
        }
        OpenLayers.Event.stop(evt);
    },

    onHOverHandler: function (evt) {
        if (this.popup && ! this.popup.visible()) {
            // fix attributes if popup was manually closed
            this.clicked = false;
        }
        if (this.popup == null || ! this.downloaded) {
            this.popup = this.createPopup();
            this.popup.autoSize = true;
            this.popup.panMapIfOutOfView = false; //document.myform.autopan.checked;
            this.popup.minSize = new OpenLayers.Size(180, 30);
            this.popup.maxSize = new OpenLayers.Size(280, 300);
            map.addPopup(this.popup);
            var content = generateBubble(this.popup.feature.data.marker_id, "downloading");
            this.popup.setContentHTML(content);
            OpenLayers.Request.GET({
                url: 'marker/' + this.popup.feature.data.marker_id,
                success: function (ajaxRequest) {
                    var template = $('#popupTpl').html();
                    var resp = JSON.parse(ajaxRequest.responseText);
                    var content = Mustache.render(template, resp);
                    this.popup.setContentHTML(content);
                    this.downloaded = true;

                    fixBubbleHeigth(this.popup.feature.data.marker_id);

                },
                failure: function (ajaxRequest) {
                    var content = generateBubble(this.popup.feature.data.marker_id, "error " + ajaxRequest.status);
                    this.popup.setContentHTML(content);
                },
                scope: this
            });
        }
        this.popup.show();
        this.activePopup = true;
        OpenLayers.Event.stop(evt);
    },

    onOutHandler: function (evt) {
        if (!this.clicked) {
            this.popup.hide();
        }
        this.activePopup = false;
        OpenLayers.Event.stop(evt);
    },

    clearFeatures: function () {
        if (this.features != null) {
            while (this.features.length > 0) {
                var feature = this.features[0];
                OpenLayers.Util.removeItem(this.features, feature);
                feature.destroy();
            }
        }
    },

    CLASS_NAME: "OpenLayers.Layer.DynPoi"
});
