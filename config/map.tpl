Content-Type: text/html; charset=utf-8

<!doctype html>
<html>

<head>
  <title>#title#</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <meta name="description" content="Contrôle, vérification et correction d'erreurs d'OpenStreetMap">
  <!-- <link rel="stylesheet" type="text/css" href="http://openlayers.org/dev/theme/default/style.css"> -->
  <link rel="stylesheet" type="text/css" href="style.css">
  <link rel="stylesheet" type="text/css" href="style-ol.css">
  <script type="text/javascript" src="../OpenLayers-2.8/OpenLayers.js"></script>
  <script type="text/javascript" src="http://www.openstreetmap.org/openlayers/OpenStreetMap.js"></script>
  <script type="text/javascript" src="DynPoi.js"></script>
  <script type="text/javascript" src="BetaStyles.js"></script>
  <script type="text/javascript" src="map.js"></script>
  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>

  <script type="text/javascript">
    var lat=#lat#;
    var lon=#lon#;
    var zoom=#zoom#;
    var item_levels = {};
    #item_levels#;
  </script>
</head>

<body onload="init();" onresize="handleResize();">

<iframe id="hiddenIframe" name="hiddenIframe"></iframe>

<div id="incFrameBg"></div>
<iframe id="incFrame" src="" width=780 height=540 scrolling="auto" frameborder="1" ></iframe>
<a accesskey="w" href="javascript:iFrameClose();"><img id="incFrameBt" src="images/close.png"></a>

<div id="menu">
  <a id="togglemenu" href="javascript:toggleMenu()">-</a>
  <form id="myform" name="myform" action="#">
  <input type='hidden' name='lat'    value='#lat#'>
  <input type='hidden' name='lon'    value='#lon#'>
  <input type='hidden' name='zoom'   value='#zoom#'>
  <input type='hidden' name='source' value='#source#'>
  <input type='hidden' name='user'   value='#user#'>
    <div id="need_zoom">#need_zoom#</div>
    <div id="action_links">
      <span id="level-span">
        <label for='level'>#severity#</label>
        <select id='level' onclick='javascript:change_level();'>
          <option class="level-1__" value="1"#level1#>#level1_desc#</option>
          <option class="level-12_" value="1,2"#level1,2#>#level1,2_desc#</option>
          <option class="level-123" value="1,2,3"#level1,2,3#>#level1,2,3_desc#</option>
          <option disabled="disabled"></option>
          <option class="level-_2_" value="2"#level2#>#level2_desc#</option>
          <option class="level-__3" value="3"#level3#>#level3_desc#</option> 
        </select>
      </span>
      <br>
      #check#
      <a href="javascript:set_checkboxes(true);">#check_all#</a>
      <a href="javascript:set_checkboxes(false);">#check_nothing#</a>
      <a href="javascript:toggle_checkboxes();">#check_invert#</a>
    </div>
  <div id="tests" >
  #form#
  </div>
</form>
</div>

<div id="map"></div>

