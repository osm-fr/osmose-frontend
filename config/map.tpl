Content-Type: text/html; charset=utf-8

<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>

<head>
  <title>#title#</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <link rel="stylesheet" type="text/css" href="http://openlayers.org/dev/theme/default/style.css">
  <link rel="stylesheet" type="text/css" href="style.css">
  <link rel="stylesheet" type="text/css" href="style-ol.css">
  <script type="text/javascript" src="/OpenLayers-2.8/OpenLayers.js"></script>
  <script type="text/javascript" src="http://www.openstreetmap.org/openlayers/OpenStreetMap.js"></script>
  <script type="text/javascript" src="DynPoi.js"></script>
  <script type="text/javascript" src="BetaStyles.js"></script>
  <script type="text/javascript" src="map.js"></script>

  <script type="text/javascript">
    var lat=#lat#;
    var lon=#lon#;
    var zoom=#zoom#;
  </script>
</head>

<body onload="init();" onresize="handleResize();">

<iframe style="display:none;position:absolute;" id="hiddenIframe" name="hiddenIframe"></iframe>

<div id="incFrameBg" style="opacity:0.75;visibility:hidden;position:absolute;top:0;bottom:0;left:0;right:0;background-color:#000000;z-index:1199;"></div>
<iframe id="incFrame" src="" width=780 height=540 scrolling="auto" style="position:absolute;z-index:1200;top:10;left:10;visibility:hidden;" frameborder="1" ></iframe>
<img id="incFrameBt" src="close.png" style="visibility:hidden;border:0px;position:absolute;z-index:1201;top:10;left:772;" onclick="iFrameClose();">
<a accesskey="w" style="visibility:hidden;" href="javascript:iFrameClose();">iframeclose</a>

<div id="menu">
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
</div>

<div id="map" style="position:absolute;"></div>

<div id="bottom_links">
  <center><font size=-1>
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
  <a href="/utils/last-update.py">statistiques</a>
  </font></center>
</div>

</body>
</html>

