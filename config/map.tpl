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
    var item_levels = {};
    #item_levels#;
  </script>
</head>

<body onload="init();" onresize="handleResize();">

<iframe id="hiddenIframe" name="hiddenIframe"></iframe>

<div id="incFrameBg"></div>
<iframe id="incFrame" src="" width=780 height=540 scrolling="auto" frameborder="1" ></iframe>
<img id="incFrameBt" src="close.png" onclick="iFrameClose();">
<a accesskey="w" style="visibility:hidden;" href="javascript:iFrameClose();">iframeclose</a>

<div id="menu">
  <center><div id="need_zoom">
    <br><br>#need_zoom#<br><br>
  </div></center>
  <center><div id="action_links">
      #check#
      <a href="javascript:set_checkboxes(true);">#check_all#</a>
      <a href="javascript:set_checkboxes(false);">#check_nothing#</a>
      <a href="javascript:toggle_checkboxes();">#check_invert#</a>
  </div></center>
  <form id="myform" name="myform" action="#">
      <input type='hidden' name='lat'    value='#lat#'>
      <input type='hidden' name='lon'    value='#lon#'>
      <input type='hidden' name='zoom'   value='#zoom#'>
      <input type='hidden' name='source' value='#source#'>
      <input type='hidden' name='user'   value='#user#'>
      <center>
      <label for='level'>Level choice</label>
      <select id='level' onclick='javascript:change_level();'>
        <option value=""#level_all#>#level_all_str#</option>
        <option value="1"#level1#>1</option>
        <option value="2"#level2#>2</option>
        <option value="1,2"#level1,2#>1+2</option>
        <option value="3"#level3#>3</option>
        <option value="1,2,3"#level1,2,3#>1+2+3</option>
      </select>
      </center>
      #form#
  </form>
</div>

<div id="map"></div>

