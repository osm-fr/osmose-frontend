<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="{{translate.languages[0]}}">
<head>
  <title>Osmose - {{_("Map")}}</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <meta name="description" content="Contrôle, vérification et correction d'erreurs d'OpenStreetMap">
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='css/style.css')}}">
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='/map/leaflet/leaflet.css')}}" />
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='/map/leaflet-sidebar/src/L.Control.Sidebar.css')}}">
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename='/map/style.css')}}">
  <script id="popupTpl" type="text/template" src="{{get_url('static', filename='/tpl/popup.tpl')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/js/jquery-1.7.2.min.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/js/mustache.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/leaflet/leaflet-src.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/leaflet-plugins/control/Permalink.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/leaflet-plugins/control/Permalink.Layer.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/Permalink.Overlay.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/Permalink.Item.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/leaflet-plugins/layer/tile/Bing.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/layers.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/leaflet-sidebar/src/L.Control.Sidebar.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/Osmose.Menu.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/Osmose.Marker.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/map.js')}}"></script>
  <script type="text/javascript" src="{{get_url('static', filename='/map/menu.js')}}"></script>
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
<body>

<iframe id="hiddenIframe" name="hiddenIframe"></iframe>

<div id="incFrameBg"></div>
<iframe id="incFrame" src="" width=780 height=540 scrolling="auto" frameborder="1" ></iframe>
<a accesskey="w" href="javascript:iFrameClose();"><img id="incFrameBt" src="../images/close.png" alt="close menu"></a>

<div id="menu">
  <a id="togglemenu">-</a>
  <form id="myform" name="myform" action="#">
  <input type='hidden' name='lat' value='{{lat}}'>
  <input type='hidden' name='lon' value='{{lon}}'>
  <input type='hidden' name='zoom' value='{{zoom}}'>
  <input type='hidden' name='source' value='{{source}}'>
  <input type='hidden' name='class' value='{{classs}}'>
  <input type='hidden' name='useDevItem' value='{{useDevItem}}'>
  <input type='hidden' name='username' value='{{username}}'>
  <input type='hidden' name='country' value='{{country}}'>
  <input type='hidden' name='tags' value='{{tags}}'>
    <div id="need_zoom">{{_("no bubbles at this zoom factor")}}</div>
    <div id="action_links">
      <span id="level-span">
        <label for='level'>{{_("Severity")}}</label>
        <select id='level'>
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
      <a href="#" class="toggleAllItem" data-view="all">{{_("all")}}</a>
      <a href="#" class="toggleAllItem" data-view="nothing">{{_("nothing")}}</a>
      <a href="#" class="invertAllItem">{{_("invert")}}</a>
    </div>
  <div id="tests" >
%it = set()
%for categ in categories:
    <div class="test_group" id="categ{{categ["categ"]}}">
    <h1><a href="#" class="toggleCateg">{{categ["menu"]}}</a>
    <span class="count">{{len([x for x in categ["item"] if x["item"] in active_items])}}/{{len(categ["item"])}}</span>
    <a href="#" class="toggleAllItem" data-view="all">{{_("all")}}</a>
    <a href="#" class="toggleAllItem" data-view="nothing">{{_("nothing")}}</a></h1>
    <ul>
%    for err in categ["item"]:
%        it.add(err["item"])
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
            <input type='checkbox' id='item{{err["item"]}}' name='item{{err["item"]}}' {{! {True:" checked=\"checked\"", False:""}[err["item"] in active_items]}}>
            <a target="_blank" href="../errors/?item={{err["item"]}}">{{err["menu"]}}</a>
        </li>
%    end
    </ul>
    </div>
%end
%unactiveItem = set(active_items) - it
%if unactiveItem:
    <div class="test_group" id="categUnactiveItem" style="display: none">
    <h1><span id="categUnactiveItem_count">1/0</span></h1>
    <ul>
%    for item in unactiveItem:
        <li id='item_desc{{item}}'>
            <input type='checkbox' id='{{item}}' name='item{{item}}' checked="checked">
            <a target="_blank" href="../errors/?item={{err["item"]}}">{{item}}</a>
        </li>
%    end
    </ul>
    </div>
%end
  </div>
</form>
</div>

<div id="map"></div>

<div id='top_links'>
<ul id="topmenu">
<li><a href='#'>{{_("Change language")}} ▼</a>
<ul class="submenu">
%for l in allowed_languages:
%    if translate.languages[0] == l:
%        s = " class='bold'"
%    else:
%        s = ""
%    end
  <li{{!s}}><a href="{{"http://" + website + "/" + l + request.path + "?" + request.query_string}}">{{l}}</a></li>
%end
</ul>
</li>

%for u in urls:
 <li><a href="{{u[1]}}">{{u[0]}}</a></li>
%end

<li><a href='#'>{{_("Help")}} ▼</a>
<ul class="submenu">
%for u in helps:
 <li><a href="{{u[1]}}">{{u[0]}}</a></li>
%end
</ul>
</li>

%delay_status = "normal" if delay < 1.1 else "warning" if delay < 1.6 else "error"
%delay = "%0.2f" % delay
<li><a href="../control/update" class="delay-{{delay_status}}">{{_("Delay: %sd") % delay}}</a></li>
</ul>
</div>

<script type="text/javascript">
$(function() {
  init_map();
});
</script>

</body>
</html>
