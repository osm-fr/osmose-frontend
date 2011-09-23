<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>

<head>
  <title>#title#</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <link rel="stylesheet" type="text/css" href="http://openlayers.org/dev/theme/default/style.css">
  <link rel="stylesheet" type="text/css" href="../style.css">
  <link rel="stylesheet" type="text/css" href="../style-ol.css">
  <!--<script type="text/javascript" src="http://www.openlayers.org/api/OpenLayers.js"></script>-->
  <script type="text/javascript" src="http://osm1.crans.org/OpenLayers-2.8/OpenLayers.js"></script>
  <script type="text/javascript" src="http://www.openstreetmap.org/openlayers/OpenStreetMap.js"></script>
  <script type="text/javascript" src="../DynPoi.js"></script>
  <script type="text/javascript" src="../BetaStyles.js"></script>

  <script type="text/javascript">
    var lat=#lat#;
    var lon=#lon#;
    var zoom=#zoom#;
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
      
      var layerTilesAtHome = new OpenLayers.Layer.OSM.Osmarender("Osmarender");
      map.addLayer(layerTilesAtHome);

//       var layerOpenSeaMap = new OpenLayers.Layer.TMS("OpenSeaMap", "http://tiles.openseamap.org/seamark/", { numZoomLevels: 18, type: 'png', getURL: getTileURL, isBaseLayer: false, displayOutsideMaxExtent: true});
//      map.addLayer(layerOpenSeaMap);
                 
      //*****************************************************
      // Layers de beta.letuffe.org

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
        var name = 'beta - ' + all_available_styles[idx];
        var l = new OpenLayers.Layer.TMS(
	  name,
	  ["http://beta.letuffe.org/tiles/renderer.py/"+idx+"/"],
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
        var name = 'beta - ' + all_available_overlays[idx];
	var overlay = new OpenLayers.Layer.TMS( 
          name, 
	  ["http://beta.letuffe.org/tiles/renderer.py/"+idx+"/"],
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

      //******************************************************
      
      pois = new OpenLayers.Layer.DynPoi("Erreurs Osmose", {
        location:"dynpoi.py",
        projection: new OpenLayers.Projection("EPSG:4326")} );
      map.addLayer(pois);
      
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
	      
      var divGauche  = document.getElementById('gauche').style;
      var divDroite  = document.getElementById('map').style;
      var divBas     = document.getElementById('bas').style;
      
      if (document.myform.source.value == '') {
        g = 280;
      } else {
	g = 0;
      }
      
      divGauche.width  = g + "px";
      divGauche.height = (globalHeight - 20) + "px";
      divGauche.left   = 0 + "px";
      divGauche.top    = 0 + "px";
      
      divDroite.width  = (globalWidth - g) + "px";
      divDroite.height = (globalHeight - 20) + "px";
      divDroite.left   = g + "px";
      divDroite.top    = 0 + "px";
      
      divBas.width     = globalWidth + "px";
      divBas.height    = 20 + "px";
      divBas.left      = 0 + "px";
      divBas.top       = (globalHeight - 20) + "px";
    
      divBas.display   = 'inline';
    
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
    
    // Load URL in iFrame
    function iFrameLoad(url) {
      document.getElementById('incFrame').src = url;
      document.getElementById('incFrame').style.visibility = null;
      document.getElementById('incFrameBt').style.visibility = null;
      document.getElementById('incFrameBg').style.visibility = null;
    }
    function iFrameClose(url) {
      document.getElementById('incFrame').style.visibility   = 'hidden';
      document.getElementById('incFrameBt').style.visibility = 'hidden';
      document.getElementById('incFrameBg').style.visibility = 'hidden';
    }
    
  </script>
</head>

<body onload="init();" onresize="handleResize();">

<iframe style="display:none;position:absolute;" id="hiddenIframe" name="hiddenIframe"></iframe>

<div id="incFrameBg" style="opacity:0.75;visibility:hidden;position:absolute;top:0;bottom:0;left:0;right:0;background-color:#000000;z-index:1199;"></div>
<iframe id="incFrame" src="" width=780 height=540 scrolling="auto" style="position:absolute;z-index:1200;top:10;left:10;visibility:hidden;" frameborder="1" ></iframe>
<img id="incFrameBt" src="../close.png" style="visibility:hidden;border:0px;position:absolute;z-index:1201;top:10;left:772;" onclick="iFrameClose();">
<a accesskey="w" style="visibility:hidden;" href="javascript:iFrameClose();">iframeclose</a>

<!--<div id="gauche" style="background-color:#FF5555;position:absolute;overflow-y:scroll;">-->
<div id="gauche" style="position:absolute;overflow-y:scroll;">
  <!--<center><font color="#AA0000"><b><br>!!! NE PAS UTILISER !!!<br>!!! BASE DE TEST !!!<br><br></b></font></center>-->
  <center><div id="need_zoom">
    <br><br>#need_zoom#<br><br>
  </div></center>
  <center><div id="action_links">
      Global : 
      <a href="javascript:set_checkboxes(true);">Tout</a> 
      <a href="javascript:set_checkboxes(false);">Rien</a>
      <a href="javascript:toggle_checkboxes();">Inverser</a>
  </div></center>
  <form id="myform" name="myform" action="#">
      <input type='hidden' name='lat'    value='#lat#'>
      <input type='hidden' name='lon'    value='#lon#'>
      <input type='hidden' name='zoom'   value='#zoom#'>
      <input type='hidden' name='source' value='#source#'>
      <input type='hidden' name='user'   value='#user#'>
      #form#
  </form>
  <!--<br>
  <div id="bottom_links">
      <a id="stats" href="/cgi-bin/last-update.py">statistiques</a>
  </div>-->
</div>

<div id="map" style="position:absolute;"></div>

<div id="bas" style="background-color:#DDDDDD;position:absolute;display: none;">
  <center><font size=-1>
  <!--<a href="osmose.py">mode texte</a>
  - -->
  <!--<a href="/clc">polygones clc</a>
  - -->
  <a href="http://wiki.openstreetmap.org/wiki/FR:Osmose">Aide</a>
  - 
  <a href="/text">par utilisateur</a>
  - 
  <a href="http://clc.openstreetmap.fr">clc</a>
  - 
  <a href="http://analyser.openstreetmap.fr/">analyseur de relation</a>
  - 
  <a href="http://geodesie.openstreetmap.fr/">géodésie</a>
  - 
  <a href="http://www.openstreetmap.fr/">openstreetmap.fr</a>
  -
  <a href="/copyright.html">copyright</a>
  -
  <a href="https://gitorious.org/osmose">sources</a>
  -
  <a href="last-update.py">statistiques</a>
  </font></center>
</div>

</body>
</html>

