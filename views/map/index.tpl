<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html lang="{{translate.languages[0]}}">
<head>
  <title>Osmose - {{_("Map")}}</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <meta name="description" content="Contrôle, vérification et correction d'erreurs d'OpenStreetMap">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
%for css in assets['css_map'].urls():
  <link rel="stylesheet" type="text/css" href="{{get_url('static', filename=css)}}">
%end
  <script id="popupTpl" type="text/template" src="{{get_url('static', filename='/tpl/popup.tpl')}}"></script>
  <script id="editorTpl" type="text/template" src="{{get_url('static', filename='/tpl/editor.tpl')}}"></script>
%for js in assets['js_map'].urls():
  <script type="text/javascript" src="{{get_url('static', filename=js)}}"></script>
%end
  <script type="text/javascript">
    var lat={{lat}};
    var lon={{lon}};
    var zoom={{zoom}};
    var item_levels = {};
%for (l, i) in item_levels.iteritems():
    item_levels["{{l}}"] = {{list(i)}};
%end
    var item_tags = {};
%for (t, i) in item_tags.iteritems():
    item_tags["{{t}}"] = {{list(i)}};
%end
  </script>
</head>
<body>
<iframe id="hiddenIframe" name="hiddenIframe"></iframe>
<div id="menu">
  <a href="#" id="togglemenu">-</a>
  <form id="myform" name="myform" action="#">
  <input type='hidden' name='lat' value='{{lat}}'>
  <input type='hidden' name='lon' value='{{lon}}'>
  <input type='hidden' name='zoom' value='{{zoom}}'>
  <input type='hidden' name='source' value='{{source}}'>
  <input type='hidden' name='class' value='{{classs}}'>
  <input type='hidden' name='useDevItem' value='{{useDevItem}}'>
  <input type='hidden' name='username' value='{{username}}'>
  <input type='hidden' name='country' value='{{country}}'>
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
      <span id="fixable-span">
        <label for='fixable'>{{_("Fixable")}}</label>
        <select id="fixable" title="{{_("Show only markers with correction suggestions")}}">
          <option value=""></option>
          <option value="online"{{!fixable_selected['online']}}>{{_("Online")}}</option>
          <option value="josm"{{!fixable_selected['josm']}}>JOSM</option>
        </select>
      </span>
      <span id="tags-span">
        <label for='tags'>{{_("Topic")}}</label>
        <select id='tags'>
          <option value=""></option>
%for tag in tags:
          <option value="{{tag}}" {{!tags_selected[tag]}}>{{_(tag)}}</option>
%end
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

<div id="map">
  <div id="spinner">
    <img src='../images/throbbler-big.gif' alt='downloading'>
  </div>
</div>

<div id='top_links'>
<ul id="topmenu">
<li id="menu-lang"><a href='#'>{{_("Change language")}} ▼</a>
<ul class="submenu">
%for (k, v) in languages_name.items():
%    if translate.languages[0] == k:
%        s = " class='bold'"
%    else:
%        s = ""
%    end
  <li{{!s}}><a href="{{"http://" + website + "/" + k + request.path + "?" + request.query_string}}">{{v}} ({{k}})</a></li>
%end
</ul>
</li>

%for u in urls:
 <li id="menu-{{u[0]}}"><a href="{{u[2]}}">{{u[1]}}</a></li>
%end

<li id="menu-export"><a href='#'>{{_("Export")}} ▼</a>
<ul class="submenu">
  <li><a href="../errors/" target="_blank">{{_("Html list")}}</a></li>
  <li><a href="../errors.josm" target="hiddenIframe">JOSM</a></li>
  <li><a href="../errors.rss" target="_blank">RSS</a></li>
  <li><a href="../errors.gpx">GPX</a></li>
  <li><a href="../api/0.2/errors" target="_blank">Json</a></li>
  <li><a href="markers" target="_blank">GeoJson</a></li>
</ul>

<li id="menu-help"><a href='#'>{{_("Help")}} ▼</a>
<ul class="submenu">
%for u in helps:
 <li><a href="{{u[1]}}">{{u[0]}}</a></li>
%end
</ul>
</li>

%delay_status = "normal" if delay < 1.1 else "warning" if delay < 1.6 else "error"
%delay = "%0.2f" % delay
<li id="menu-delay"><a href="../control/update" class="delay-{{delay_status}}">{{_("Delay: %sd") % delay}}</a></li>

<li id="menu-user">
%if user:
  <a href="../byuser/{{user}}">{{user}} ({{user_error_count[1]+user_error_count[2]+user_error_count[3]}}) ▼</a>
  <ul class="submenu">
    <li><a href="../byuser/{{user}}?level=1">{{_("Level %d errors (%d)") % (1, user_error_count[1])}}</a></li>
    <li><a href="../byuser/{{user}}?level=2">{{_("Level %d errors (%d)") % (2, user_error_count[2])}}</a></li>
    <li><a href="../byuser/{{user}}?level=3">{{_("Level %d errors (%d)") % (3, user_error_count[3])}}</a></li>
    <li><a href="../logout">{{_("Logout")}}</a></li>
  </ul>
%else:
  <a href="../login">{{_("Login")}}</a>
%end
</li>

<li id="menu-editor-save" style="display:none">
  <a href="#">{{_("Save")}} (<span id="menu-editor-save-number"></span>)</a>
</li>

</ul>
</div>

<script type="text/javascript">
$(function() {
  init_map();
});
</script>

<div id="editor" data-user="{{not not user}}"><p>{{_("You must be logged in order to use the tag editor")}}</p><a href="../login">{{_("Login")}}</a></div>

<div id="dialog_editor_save_popup" title="{{_("Save changeset")}}" data-button_cancel="{{_("Cancel")}}" data-button_save="{{_("Save")}}" style="display:none">
  <p>{{_("Objects edited:")}}&nbsp;<span id="editor-modify-count"></span></p>
  <p>{{_("Objects deleted:")}}&nbsp;<span id="editor-delete-count"></span></p>
  <form id="editor_save_form">
    <label for="comment">{{_("Comment")}}</label><input type="text" name="comment" id="comment" value="{{_("Fix with Osmose")}}"/>
    <br/><br/>
    <label for="source">{{_("Source")}}</label><input type="text" name="source" id="source" value="Osmose"/>
    <br/><br/>
    <label for="type">{{_("Type")}}</label><input type="text" name="type" id="type" value="fix"/>
    <br/><br/>
    <input type="checkbox" name="reuse_changeset" id="reuse_changeset" checked="checked"/><label for="reuse_changeset">{{_("Reuse changeset")}}</label>
  </form>
</div>

</body>
</html>
