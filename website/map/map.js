    var pois=null;
    var map=null;
    var plk=null;
    
    //----------------------------------------//
    // init map function                      //
    //----------------------------------------//

    function init() {
      map = new OpenLayers.Map ("map", {
        controls:[
          new OpenLayers.Control.Navigation(),
          new OpenLayers.Control.PanZoomBar(),
          new OpenLayers.Control.LayerSwitcher(),
	  new OpenLayers.Control.Attribution(),
          new OpenLayers.Control.MousePosition()],

	  maxExtent: new OpenLayers.Bounds(-20037508,-20037508,20037508,20037508),
	  maxResolution: 156543,
	  
	  numZoomLevels: 20,
	  units: 'm',
	  projection: new OpenLayers.Projection("EPSG:900913"),
	  displayProjection: new OpenLayers.Projection("EPSG:4326"),
	  theme: null
      });

      plk = new OpenLayers.Control.Permalink("permalink");
      map.addControl(plk);	    

      var layerMapnik = new OpenLayers.Layer.OSM.Mapnik("Mapnik");
      map.addLayer(layerMapnik);

      var layerMapquest = new OpenLayers.Layer.XYZ( 
          "MapQuest Open", 
          ["http://otile1.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png", "http://otile2.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png", "http://otile3.mqcdn.com/tiles/1.0.0/osm/${z}/${x}/${y}.png" ],
          {type:'png',
	  transitionEffect: 'resize',
          displayOutsideMaxExtent: true }, {'buffer':0} );
      layerMapquest.attribution += " - Tiles Courtesy of <a href=\"http://www.mapquest.com/\" target=\"_blank\">MapQuest</a> <img src=\"http://developer.mapquest.com/content/osm/mq_logo.png\">";
      map.addLayer(layerMapquest);

      var layerOPNVKarte = new OpenLayers.Layer.XYZ( 
          "ÖPNV Karte", 
          ["http://tile.memomaps.de/tilegen/${z}/${x}/${y}.png"],
          {type:'png',
	  transitionEffect: 'resize',
          displayOutsideMaxExtent: true }, {'buffer':0} );
      map.addLayer(layerOPNVKarte);

//      var layerTilesAtHome = new OpenLayers.Layer.OSM.Osmarender("Osmarender");
//      map.addLayer(layerTilesAtHome);

//       var layerOpenSeaMap = new OpenLayers.Layer.TMS("OpenSeaMap", "http://tiles.openseamap.org/seamark/", { numZoomLevels: 18, type: 'png', getURL: getTileURL, isBaseLayer: false, displayOutsideMaxExtent: true});
//      map.addLayer(layerOpenSeaMap);

                 
      //*****************************************************
      // Layers de layers.openstreetmap.fr

      function get_osm_url (bounds) {
        var res = this.map.getResolution();
	var x = Math.round ((bounds.left - this.maxExtent.left) / (res * this.tileSize.w));
        var y = Math.round ((this.maxExtent.top - bounds.top) / (res * this.tileSize.h));
        var z = this.map.getZoom();
        var limit = Math.pow(2, z);
        if (y < 0 || y >= limit)
        {
          return null;
        } else {
          // x = ((x % limit) + limit) % limit;
	  return this.url + z + "/" + x + "/" + y + "." + this.type; 
        }
      }

      /* Base layers inclusion */
      var layers = [];
      for ( var idx in all_available_styles ) {
        var name = all_available_styles[idx];
        var l = new OpenLayers.Layer.TMS(
	  name,
	  ["http://layers.openstreetmap.fr/tiles/renderer.py/"+idx+"/"],
	  { type:'jpeg',
	    getURL: get_osm_url,
            transitionEffect: 'resize',
            displayOutsideMaxExtent: true },
	  { 'buffer':1
	  }
	);
	layers.push(l);
      }
		  
      /* Transparent overlays (must be png with alpha channel) */
      var layerOpenSeaMap = new OpenLayers.Layer.TMS(
              "OpenSeaMap",
              "http://tiles.openseamap.org/seamark/",
              { numZoomLevels: 18, 
                type: 'png',
                getURL: get_osm_url,
                isBaseLayer: false,
                visibility: false,
                displayOutsideMaxExtent: true }
             );
      map.addLayer(layerOpenSeaMap);
 
      var layerODBL = new OpenLayers.Layer.TMS(
              "ODBL",
              "http://osm.informatik.uni-leipzig.de/osm_tiles2/",
              { numZoomLevels: 18, 
                type: 'png',
                getURL: get_osm_url,
                isBaseLayer: false,
                visibility: false,
                displayOutsideMaxExtent: true }
             );
      map.addLayer(layerODBL);
 
      for ( var idx in all_available_overlays ) {
        var name = all_available_overlays[idx];
	var overlay = new OpenLayers.Layer.TMS( 
          name, 
	  ["http://layers.openstreetmap.fr/tiles/renderer.py/"+idx+"/"],
	  { type:'png',
	    getURL: get_osm_url, 
            displayOutsideMaxExtent: true,
	    'buffer':1,
	    isBaseLayer: false,
	    visibility: false}
	  );
        layers.push(overlay);
      }
      
      map.addLayers(layers);

      /* Must be the last layers so that markers are above any other layers */
      pois = new OpenLayers.Layer.DynPoi("Erreurs Osmose", {
        location:"dynpoi.py",
        projection: new OpenLayers.Projection("EPSG:4326")} );
      map.addLayer(pois);

      //******************************************************
      
     
      var lonLat = new OpenLayers.LonLat(lon, lat).transform(new OpenLayers.Projection("EPSG:4326"), map.getProjectionObject());
      map.setCenter(lonLat, zoom);

      map.events.register("moveend", map, function() {
        var pos = this.getCenter().clone();
        var lonlat = pos.transform(this.getProjectionObject(), new OpenLayers.Projection("EPSG:4326"));
        document.myform.lat.value  = lonlat.lat
        document.myform.lon.value  = lonlat.lon
        document.myform.zoom.value =this.getZoom();
        if (document.myform.source.value == '') {
	  if (this.getZoom()<6) {
	    document.getElementById('need_zoom').style.display    = 'inline';
	    document.getElementById('action_links').style.display = 'none';
	    document.getElementById('myform').style.display       = 'none';
	  } else {
	    document.getElementById('need_zoom').style.display    = 'none';
	    document.getElementById('action_links').style.display = 'inline';
	    document.getElementById('myform').style.display       = 'inline';
	  }
	}
        pois.loadText();
      });
      
      handleResize();
      change_level_display();

    }

    function resizeMap() {
      
      var centre = map.getCenter();
      var zoom   = map.getZoom();
      //var left   = $("sidebar").offsetWidth;
      
      var globalWidth  = 800;
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

      if( typeof( window.innerWidth ) == 'number' ) {
        //Non-IE
        globalWidth = window.innerWidth;
        globalHeight = window.innerHeight;
      } else if( document.documentElement && ( document.documentElement.clientWidth || document.documentElement.clientHeight ) ) {
        //IE 6+ in 'standards compliant mode'
        globalWidth = document.documentElement.clientWidth;
	globalHeight = document.documentElement.clientHeight;
      } else if( document.body && ( document.body.clientWidth || document.body.clientHeight ) ) {
        //IE 4 compatible
        globalWidth = document.body.clientWidth;
        globalHeight = document.body.clientHeight;
      }
	      
      var divGauche  = document.getElementById('menu').style;
      var divDroite  = document.getElementById('map').style;
      
      if (document.myform.source.value != '') {
	g = 0;
      
        divGauche.width  = g + "px";
        divGauche.height = (globalHeight - 20) + "px";
      
        divDroite.width  = (globalWidth - g) + "px";
        divDroite.height = (globalHeight - 20) + "px";
        divDroite.left   = g + "px";
        divDroite.top    = 0 + "px";
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
      var i=0;
      var len=pois.features.length;
      var feature=null;
      while (i<len && feature==null) { //>
        if (pois.features[i].id == feature_id) feature=pois.features[i];
        i++;
      }
      if (state[0].checked) feature.marker.icon.setUrl("img/zap" + error_type + ".png")
      else if (state[1].checked) feature.marker.icon.setUrl("img/zapangel.png")
      else if (state[2].checked) feature.marker.icon.setUrl("img/zapdevil.png");
    }
      
    function closeBubble(marker_id) {
      var i = 0;
      var len = pois.features.length;
      var feature = null;
      while (i<len && feature==null) {
        if (pois.features[i].data.marker_id == marker_id) feature = pois.features[i];
        i++;
      }
      feature.marker.events.triggerEvent("mousedown");
    }
    
    //----------------------------------------//
    // function for left menu                 //
    //----------------------------------------//
        
    // Change value for all checkboxes
    function set_checkboxes(new_value) {
      for (var i = 0; i < document.myform.elements.length; ++i) {
        var el=document.myform.elements[i];
        if (el.type == "checkbox" && el.name.match(/item[0-9]+/)) {
          el.checked=new_value;
        }
      }
      groupes = document.getElementsByClassName('test_group');
      for (i = 0 ; i<groupes.length ; i++) {
        updateCountTestsSpan(groupes[i]);
      }
      pois.loadText();
    }

    // Toggle value for all checkboxes
    function toggle_checkboxes() {
      for (var i = 0; i < document.myform.elements.length; ++i) {
        var el=document.myform.elements[i];
        if (el.type == "checkbox" && el.name.match(/item[0-9]+/)) {
          el.checked=!el.checked;
        }
      }
      groupes = document.getElementsByClassName('test_group');
      for (i = 0 ; i<groupes.length ; i++) {
        updateCountTestsSpan(groupes[i]);
      }
      pois.loadText();
    }

    // Update checkbox count
    function updateCountTestsSpan(d) {
      boxes = d.getElementsByTagName('input');
      count_checked = 0;
      count_tests = 0;
      for (i = 0 ; i<boxes.length ; i++) {
        if (boxes[i].type == "checkbox" && boxes[i].name.match(/item[0-9]+/) && boxes[i].checked) 
          count_checked++;
        count_tests++;
      }
      s = document.getElementById(d.id+'_count');
      if (s) s.innerHTML = count_checked+'/'+count_tests;
    }

    // Click on a checkbox
    function checkbox_click(cb) {
      updateCountTestsSpan(cb.parentNode);
      pois.loadText();
    }

    // Show or hide a group of tests
    function toggleCategDisplay(id) {
      d = document.getElementById(id);
      if (d.style.height == '20px') {
        // show
        d.style.height = null;
        d.style.overflow = null;
      } else {
        // hide
        d.style.height = '20px';
        d.style.overflow = 'hidden';
      }
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
      for (i = 0 ; i<cb.length ; i++) {
        if (cb[i].type == "checkbox" && cb[i].name.match(/item[0-9]+/)) {
          cb[i].checked = showhide;
        }
      }
      updateCountTestsSpan(d);
      pois.loadText();
    }

    // Change level
    function change_item_display(l, enable) {
      disabled = !enable;
      hidden = enable ? null : "hidden";
      color = enable ? "black" : "#999999";
      for (var i = 0; i < item_levels[l].length; ++i) {
        var el = document.getElementById('item' + item_levels[l][i]);
        el.style.visibility=hidden;
//        el.disabled=disabled;
        el = document.getElementById('item_desc' + item_levels[l][i]);
        el.style.color=color;
        el = el.getElementsByTagName('a')[0];
        el.style.color=color;
      }
    }

    function change_level_display() {
      var new_level = document.getElementById('level').value;

      if (new_level == "") {
        change_item_display("1,2,3", true);
      } else {
        change_item_display("1,2,3", false);
        change_item_display(new_level, true);
      }
    }

    function change_level() {
      change_level_display();
      pois.loadText();
    }
    
    // Load URL in iFrame
    function iFrameLoad(url) {
      document.getElementById('incFrame').src = url;
      document.getElementById('incFrame').style.display = 'inline';
      document.getElementById('incFrameBt').style.display = 'inline';
      document.getElementById('incFrameBg').style.display = 'inline';
    }
    function iFrameClose(url) {
      document.getElementById('incFrame').style.display   = 'none';
      document.getElementById('incFrameBt').style.display = 'none';
      document.getElementById('incFrameBg').style.display = 'none';
    }

    function setCookie(c_name,value,exdays) {
      var exdate=new Date();
      exdate.setDate(exdate.getDate() + exdays);
      var c_value=escape(value) + ((exdays==null) ? "" : "; path=/; expires="+exdate.toUTCString());
      document.cookie=c_name + "=" + c_value;
    }

    function set_lang(lang) {
      setCookie("lang", lang, 30);
      window.location = document.URL;
    }
