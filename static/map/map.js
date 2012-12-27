var pois = null;
var map = null;
var plk = null;
/* used to store old zoom factore to triger events when "going above" treshold */
var oldzoom = -1;
var heat = null;
var poisParams = null;

//----------------------------------------//
// init map function                      //
//----------------------------------------//

function init() {
    map = new OpenLayers.Map("map", {
        controls: [
        new OpenLayers.Control.Navigation(),
        new OpenLayers.Control.PanZoomBar(),
        new OpenLayers.Control.LayerSwitcher(),
        new OpenLayers.Control.Attribution(),
        new OpenLayers.Control.MousePosition()],

        maxExtent: new OpenLayers.Bounds(-20037508, - 20037508, 20037508, 20037508),
        maxResolution: 156543,

        numZoomLevels: 20,
        units: 'm',
        projection: new OpenLayers.Projection("EPSG:900913"),
        displayProjection: new OpenLayers.Projection("EPSG:4326"),
        theme: null
    });

    plk = new OpenLayers.Control.Permalink("permalink");
    map.addControl(plk);

    var osm_attribution = '© les contributeurs d’<a href="http://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a>'

    var layerMapnik = new OpenLayers.Layer.OSM("Mapnik", ["http://a.tile.openstreetmap.org/${z}/${x}/${y}.png", "http://b.tile.openstreetmap.org/${z}/${x}/${y}.png", "http://c.tile.openstreetmap.org/${z}/${x}/${y}.png"], {
        transitionEffect: 'resize',
        attribution: osm_attribution,
    });
    map.addLayer(layerMapnik);

    var layerMapquest = new OpenLayers.Layer.OSM("MapQuest Open", ["http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png", "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png", "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png"], {
        transitionEffect: 'resize',
        attribution: osm_attribution + " - Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\">",
    });
    map.addLayer(layerMapquest);

    var layerOPNVKarte = new OpenLayers.Layer.OSM("ÖPNV Karte", ["http://tile.memomaps.de/tilegen/${z}/${x}/${y}.png"], {
        transitionEffect: 'resize',
    });
    map.addLayer(layerOPNVKarte);

    var bing = new OpenLayers.Layer.Bing({
        transitionEffect: 'resize',
        name: "Bing",
        type: "Aerial",
        key: "AmQcQsaJ4WpRqn2_k0rEToboqaM1ind8HMmM0XwKwW9R8bChmHEbczHwjnjFpuNP",
    });
    map.addLayer(bing);

    var layerWhite = new OpenLayers.Layer.XYZ(
        "White background",
        ["http://a.layers.openstreetmap.fr/blanc.png"],
        {
            attribution: "",
            sphericalMercator: true,
            wrapDateLine: true,
            transitionEffect: "resize",
            buffer: 0,
        }
    );
    map.addLayer(layerWhite);


    //var layerTilesAtHome = new OpenLayers.Layer.OSM.Osmarender("Osmarender");
    //map.addLayer(layerTilesAtHome);

    //var layerOpenSeaMap = new OpenLayers.Layer.TMS("OpenSeaMap", "http://tiles.openseamap.org/seamark/", { numZoomLevels: 18, type: 'png', getURL: getTileURL, isBaseLayer: false, displayOutsideMaxExtent: true});
    //map.addLayer(layerOpenSeaMap);

    //*****************************************************
    // Layers de layers.openstreetmap.fr

    /* Base layers inclusion */
    var layers = [];
    for (var idx in all_available_styles) {
        var name = all_available_styles[idx];
        var l = new OpenLayers.Layer.XYZ(
        name, ["http://a.layers.openstreetmap.fr/" + idx + "/${z}/${x}/${y}.png",
               "http://b.layers.openstreetmap.fr/" + idx + "/${z}/${x}/${y}.png",
               "http://c.layers.openstreetmap.fr/" + idx + "/${z}/${x}/${y}.png"], {
            type: 'png',
            transitionEffect: 'resize',
            displayOutsideMaxExtent: true
        }, {
            'buffer': 1
        });
        layers.push(l);
    }

    /* Transparent overlays (must be png with alpha channel) */
    for (var idx in all_available_overlays) {
        var name = all_available_overlays[idx];
        var overlay = new OpenLayers.Layer.XYZ(
        name, ["http://a.layers.openstreetmap.fr/" + idx + "/${z}/${x}/${y}.png",
               "http://b.layers.openstreetmap.fr/" + idx + "/${z}/${x}/${y}.png",
               "http://c.layers.openstreetmap.fr/" + idx + "/${z}/${x}/${y}.png"], {
            displayOutsideMaxExtent: true,
            'buffer': 1,
            isBaseLayer: false,
            visibility: false,
            attribution: osm_attribution,
        });
        layers.push(overlay);
    }

    map.addLayers(layers);

    heat = new OpenLayers.Layer.OSM("Osmose Errors Heatmap", ["heat/${z}/${x}/${y}.png"], {
        transitionEffect: 'resize',
        isBaseLayer: false,
        visibility: false
    });
    map.addLayer(heat);

    /* Must be the last layers so that markers are above any other layers */
    pois = new OpenLayers.Layer.DynPoi("Osmose Errors", {
        location: "markers",
        projection: new OpenLayers.Projection("EPSG:4326")
    });
    map.addLayer(pois);

    //******************************************************


    var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
    map.setCenter(lonLat, zoom);

    $("div#menu").data('opened', true);
    $("div#menu").css('height', '90%');

    map.events.register("moveend", map, function () {
        var pos = this.getCenter().clone();
        var lonlat = pos.transform(this.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
        document.myform.lat.value = lonlat.lat
        document.myform.lon.value = lonlat.lon
        document.myform.zoom.value = this.getZoom();
        if (this.getZoom() >= 6) {
            updateURL();
        }
        if (this.getZoom() < 6 && oldzoom >= 6) {
            $("div#need_zoom").show();
            $("div#action_links").hide();
            $("div#tests").hide();
        } else if (this.getZoom() >= 6 && oldzoom < 6) {
            $("div#need_zoom").hide();
            $("div#action_links").show();
            if ($("div#menu").data('opened')) {
                console.log('showing tests');
                $("div#tests").fadeIn();
            }
        }
        oldzoom = this.getZoom();
    });

    handleResize();
    change_level_display();

     $.ajax({
         url: $("#popupTpl").attr("src")
     }).done(function( html ) {
         $("#popupTpl").html(html);
     });
}

function resizeMap() {

    var centre = map.getCenter();
    var zoom = map.getZoom();
    //var left   = $("sidebar").offsetWidth;

    var globalWidth = 800;
    var globalHeight = 600;

    //if (parseInt(navigator.appVersion)>3) {
    //  if (navigator.appName=="Netscape") {
    //    globalWidth  = window.innerWidth;
    //    globalHeight = window.innerHeight;
    //  }
    //  if (navigator.appName.indexOf("Microsoft")!=-1) {
    //    globalWidth  = document.body.offsetWidth-22;
    //   globalHeight = document.body.offsetHeight-8;
    //  }
    //}

    if (typeof (window.innerWidth) == 'number') {
        //Non-IE
        globalWidth = window.innerWidth;
        globalHeight = window.innerHeight;
    } else if (document.documentElement && (document.documentElement.clientWidth || document.documentElement.clientHeight)) {
        //IE 6+ in 'standards compliant mode'
        globalWidth = document.documentElement.clientWidth;
        globalHeight = document.documentElement.clientHeight;
    } else if (document.body && (document.body.clientWidth || document.body.clientHeight)) {
        //IE 4 compatible
        globalWidth = document.body.clientWidth;
        globalHeight = document.body.clientHeight;
    }

    var divGauche = document.getElementById('menu').style;
    var divDroite = document.getElementById('map').style;

    if (document.myform.source.value != '') {
        closeMenu();
    }

    map.setCenter(centre, zoom);

}

function handleResize() {
    resizeMap();
}


//----------------------------------------//
// function for bubbles                   //
//----------------------------------------//

// unused ????
function repaintIcon(error_id, state, error_type) {
    var feature_id = pois.error_ids[error_id];
    var i = 0;
    var len = pois.features.length;
    var feature = null;
    while (i < len && feature == null) { //>
        if (pois.features[i].id == feature_id) feature = pois.features[i];
        i++;
    }
    if (state[0].checked) feature.marker.icon.setUrl("img/zap" + error_type + ".png")
    else if (state[1].checked) feature.marker.icon.setUrl("img/zapangel.png")
    else if (state[2].checked) feature.marker.icon.setUrl("img/zapdevil.png");
}

//----------------------------------------//
// function for left menu                 //
//----------------------------------------//

// Change value for all checkboxes
function set_checkboxes(new_value) {
    for (var i = 0; i < document.myform.elements.length; ++i) {
        var el = document.myform.elements[i];
        if (el.type == "checkbox" && el.name.match(/item[0-9]+/)) {
            el.checked = new_value;
        }
    }
    groupes = document.getElementsByClassName('test_group');
    for (i = 0; i < groupes.length; i++) {
        updateCountTestsSpan(groupes[i]);
    }
    updateURL();
}

// Toggle value for all checkboxes
function toggle_checkboxes() {
    for (var i = 0; i < document.myform.elements.length; ++i) {
        var el = document.myform.elements[i];
        if (el.type == "checkbox" && el.name.match(/item[0-9]+/)) {
            el.checked = !el.checked;
        }
    }
    groupes = document.getElementsByClassName('test_group');
    for (i = 0; i < groupes.length; i++) {
        updateCountTestsSpan(groupes[i]);
    }
    updateURL();
}

function closeMenu() {
    $("div#menu").data('opened', false);
    $("div#menu").css('height', '');
    $("div#tests").hide();
    $("#togglemenu").html('+');
}

function toggleMenu() {
    if (!$("div#menu").data('opened')) {
        $("div#menu").data('opened', true);
        $("div#menu").css('height', '90%');
        $("div#tests").show();
        $("#togglemenu").html('-');
    } else {
        closeMenu();
    }
}

// Update checkbox count
function updateCountTestsSpan(d) {
    boxes = d.getElementsByTagName('input');
    count_checked = 0;
    count_tests = 0;
    for (i = 0; i < boxes.length; i++) {
        if (boxes[i].type == "checkbox" && boxes[i].name.match(/item[0-9]+/) && boxes[i].checked) count_checked++;
        count_tests++;
    }
    s = document.getElementById(d.id + '_count');
    if (s) s.innerHTML = count_checked + '/' + count_tests;
}

// Click on a checkbox
function checkbox_click(cb) {
    updateCountTestsSpan(cb.parentNode.parentNode.parentNode);
    updateURL();
}

// Show or hide a group of tests
function toggleCategDisplay(id) {
    if ($("div#" + id).children('ul').is(':visible')) {
        $("div#" + id).children('ul').slideUp(200);
        $("div#" + id).children('h1').addClass('folded');
    } else {
        $("div#" + id).children('ul').slideDown(200);
        $("div#" + id).children('h1').removeClass('folded');
    }
    return;
}

// Show or hide an element
function toggleDisplay(id) {
    d = document.getElementById(id);
    if (d.style.visibility == 'hidden') {
        d.style.visibility = null;
    } else {
        d.style.visibility = 'hidden';
    }
}

// Check or uncheck a categ of tests.
function showHideCateg(id, showhide) {
    d = document.getElementById(id);
    cb = d.getElementsByTagName('input');
    for (i = 0; i < cb.length; i++) {
        if (cb[i].type == "checkbox" && cb[i].name.match(/item[0-9]+/)) {
            cb[i].checked = showhide;
        }
    }
    updateCountTestsSpan(d);
    updateURL();
}

// Change level
function change_item_display(l) {
    $("div#tests li").each(function () {
        id = parseInt($(this).attr('id').replace(/item_desc/, ''));
        if (jQuery.inArray(id, item_levels[l]) >= 0) {
            $("#item_desc" + id).show();
        } else {
            $("#item_desc" + id).hide();
        }
    });
    ll = l.split(',')
    for (var i=1 ; i<=3 ; i++) {
        if (ll.indexOf(i.toString())>=0) {
            $(".level-"+i).removeClass("disabled");
        } else {
            $(".level-"+i).addClass("disabled");
        }
    }
}

function change_level_display() {
    var new_level = document.getElementById('level').value;
    if (new_level == "") {
        change_item_display("1,2,3");
    } else {
        change_item_display(new_level);
    }
}

function change_level() {
    updateURL();
    change_level_display();
}

// Load URL in iFrame
function iFrameLoad(url) {
    document.getElementById('incFrame').src = url;
    document.getElementById('incFrame').style.display = 'inline';
    document.getElementById('incFrameBt').style.display = 'inline';
    document.getElementById('incFrameBg').style.display = 'inline';
}

function iFrameClose(url) {
    document.getElementById('incFrame').style.display = 'none';
    document.getElementById('incFrameBt').style.display = 'none';
    document.getElementById('incFrameBg').style.display = 'none';
}

function setCookie(c_name, value, exdays) {
    var exdate = new Date();
    exdate.setDate(exdate.getDate() + exdays);
    var c_value = escape(value) + ((exdays == null) ? "" : "; path=/; expires=" + exdate.toUTCString());
    document.cookie = c_name + "=" + c_value;
}

function set_lang(select) {
    var lang = $(select).val();
    window.location.href = "../" + lang + "/map/" + window.location.search;
}

function updateURL() {
    // items list
    var ch = "";
    if ($(".test_group :checkbox:not(:checked)").length == 0) {
        ch = "xxxx";
    } else {
        $(".test_group").each(function() {
            var id = this.id;
            v = $("h1 span", this).text().split("/");
            if (v[0] == v[1]) {
                ch += id.substring(5,6) + "xxx,";
            } else {
                $(":checked", this).each(function() {
                    ch += this.name.substr(4) + ",";
                })
            }
        })
    }
    ch = ch.replace(/,$/, '');

    var permalink = plk.element;
    permalink.href = permalink.href.replace(/&item=[-0-9x,]*/, '').replace(/\?item=[-0-9x,]*&?/, '?') + "&item=" + ch;
    permalink.href = permalink.href.replace(/&level=[-0-9x,]*/, '').replace(/\?level=[-0-9x,]*&?/, '?') + "&level=" + document.myform.level.value;

    poisParams =
        "?lat=" + document.myform.lat.value +
        "&lon=" + document.myform.lon.value +
        "&zoom=" + document.myform.zoom.value +
        "&source=" + document.myform.source.value +
        "&class=" + document.myform.class.value +
        "&user=" + document.myform.user.value +
        "&item=" + ch +
        "&level=" + document.myform.level.value;
    pois.loadText(poisParams);

    if (heat.visibility) {
        var params =
            "?source=" + document.myform.source.value +
            "&class=" + document.myform.class.value +
            "&user=" + document.myform.user.value +
            "&item=" + ch +
            "&level=" + document.myform.level.value;
        var url = "heat/${z}/${x}/${y}.png" + params;
        if (heat.url != url) {
            heat.setUrl(url);
            heat.clearGrid();
            heat.redraw();
        }
    }
}

function poisUpdate() {
    pois.loadText(poisParams);
}
