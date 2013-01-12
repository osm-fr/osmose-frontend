<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="{{translate.languages[0]}}">
<head>
  <title>Osmose - {{_("Map")}}</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <meta name="description" content="Contrôle, vérification et correction d'erreurs d'OpenStreetMap">
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='/OpenLayers/theme/default/style.css')}}">
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='/map/style.css')}}">
  <script id="popupTpl" type="text/template" src="{{get_url('static', filename='/tpl/popup.tpl')}}"></script>

  <script type="text/javascript" src="{{get_url('static', filename='/OpenLayers/OpenLayers.js')}}"></script>
  <script type="text/javascript" src="http://www.openstreetmap.org/openlayers/OpenStreetMap.js"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/DynPoi.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/BetaStyles.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/map.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/js/mustache.js')}}"></script>
  <script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.7.2/jquery.min.js"></script>
  <script type="text/javascript">
    var lat={{lat}};
    var lon={{lon}};
    var zoom={{zoom}};
    var item_levels = {};
%for (l, i) in levels.iteritems():
    item_levels["{{l}}"] = {{list(i)}};
%end
  </script>
</head>
<body onload="init();" onresize="handleResize();">

<iframe id="hiddenIframe" name="hiddenIframe"></iframe>

<div id="incFrameBg"></div>
<iframe id="incFrame" src="" width=780 height=540 scrolling="auto" frameborder="1" ></iframe>
<a accesskey="w" href="javascript:iFrameClose();"><img id="incFrameBt" src="../images/close.png" alt="close menu"></a>

<div id="menu">
  <a id="togglemenu" href="javascript:toggleMenu()">-</a>
  <form id="myform" name="myform" action="#">
  <input type='hidden' name='lat'    value='{{lat}}'>
  <input type='hidden' name='lon'    value='{{lon}}'>
  <input type='hidden' name='zoom'   value='{{zoom}}'>
  <input type='hidden' name='source' value='{{source}}'>
  <input type='hidden' name='class'  value='{{classs}}'>
  <input type='hidden' name='user'   value='{{user}}'>
    <div id="need_zoom">{{_("no bubbles at this zoom factor")}}</div>
    <div id="action_links">
      <span id="level-span">
        <label for='level'>{{_("Severity")}}</label>
        <select id='level' onclick='change_level();'>
          <option class="level-1__" value="1"{{!level_selected['1']}}>{{_("1 only")}}</option>
          <option class="level-12_" value="1,2"{{!level_selected['1,2']}}>{{_("1+2 only")}}</option>
          <option class="level-123" value="1,2,3"{{!level_selected['1,2,3']}}>{{_("all severity")}}</option>
          <option disabled="disabled"></option>
          <option class="level-_2_" value="2"{{!level_selected['2']}}>{{_("2 only")}}</option>
          <option class="level-__3" value="3"{{!level_selected['3']}}>{{_("3 only")}}</option>
        </select>
      </span>
      <br>
      {{_("Select:")}}
      <a href="javascript:set_checkboxes(true);">{{_("all")}}</a>
      <a href="javascript:set_checkboxes(false);">{{_("nothing")}}</a>
      <a href="javascript:toggle_checkboxes();">{{_("invert")}}</a>
    </div>
  <div id="tests" >
%for categ in categories:
    <div class="test_group" id="categ{{categ["categ"]}}">
    <h1><a href="javascript:toggleCategDisplay('categ{{categ["categ"]}}')">{{categ["menu"]}}</a>
    <span id="categ{{categ["categ"]}}_count">{{len([x for x in categ["item"] if x["item"] in active_items])}}/{{len(categ["item"])}}</span>
    <a href="javascript:showHideCateg('categ{{categ["categ"]}}', true)">{{_("all")}}</a>
    <a href="javascript:showHideCateg('categ{{categ["categ"]}}', false)">{{_("nothing")}}</a></h1>
    <ul>
%    for err in categ["item"]:
        <li style='background-image: url(../images/markers/marker-l-{{err["item"]}}.png)' id='item_desc{{err["item"]}}'>
            <div class="level">\\
%        p = 0
%        for i in [1,2,3]:
%            if i in err["levels"]:
<div class="level-{{i}}"><span>{{err["number"][p] if err["number"] and len(err["number"]) > p else 0}}</span></div>\\
%                p += 1
%            else:
<div></div>\\
%            end
%        end
            </div>
            <input type='checkbox' id='item{{err["item"]}}' name='item{{err["item"]}}' onclick='checkbox_click(this)' {{! {True:" checked=\"checked\"", False:""}[err["item"] in active_items]}}>
            <a target="_blank" href="../errors/?item={{err["item"]}}">{{err["menu"]}}</a>
        </li>
%    end
    </ul>
    </div>
%end
  </div>
</form>
</div>

<div id="map"></div>

<div id='bottom_links'>
<form method='get' style='display:inline; margin-right: 30px;' action=''>
{{_("Change language:")}}
<select onchange="set_lang(this)" name='language'>
    <option value=''></option>
%for l in allowed_languages:
%    if translate.languages[0] == l:
%        s = " selected='selected'"
%    else:
%        s = ""
%    end
    <option{{!s}} value='{{l}}'>{{l}}</option>
%end
</select>
</form>

%for u in urls:
 &mdash; <a href='{{u[1]}}'>{{u[0]}}</a>
%end

%delay_status = "normal" if delay < 1.1 else "warning" if delay < 1.6 else "error"
%delay = "%0.2f" % delay
<span class="delay-{{delay_status}}">{{_("Delay: %sd") % delay}}</span>
</div>

</body>
</html>
