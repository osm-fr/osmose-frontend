<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
%if 'translate' in vars():
<html lang="{{translate.languages[0]}}" dir="{{translate.direction}}">
%else:
<html>
%end
<head>
  <title>Osmose - {{_("Map")}}</title>
  <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
  <meta name="description" content="{{_("Control, verification and correction of %s issues") % main_project}}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <script id="popupTpl" type="text/template" src="{{get_url('static', filename='/tpl/popup.tpl')}}"></script>
  <script id="docTpl" type="text/template" src="{{get_url('static', filename='/tpl/doc.tpl')}}"></script>
  <script id="editorTpl" type="text/template" src="{{get_url('static', filename='/tpl/editor.tpl')}}"></script>
%from assets import assets
  <script type="text/javascript" src="{{get_url('static', filename=assets['static/map'][0])}}"></script>
  <script type="text/javascript">
    var itemLevels = {};
%for (l, i) in item_levels.iteritems():
    itemLevels["{{l}}"] = {{list(i)}};
%end
    var itemTags = {};
%for (t, i) in item_tags.iteritems():
    itemTags["{{t}}"] = {{list(i)}};
%end
    var remoteUrlRead = "{{remote_url_read}}";
  </script>
</head>
<body>
<iframe id="hiddenIframe" name="hiddenIframe"></iframe>
<div id="menu">
  <a href="#" id="togglemenu">-</a>
  <form id="myform" name="myform" action="#">
    <div id="need_zoom">{{_("no bubbles at this zoom factor")}}</div>
    <div id="action_links">
      <div id="level-span" class="form-group row">
        <label for='level' class="col-sm-3 col-form-label">{{_("Severity")}}</label>
          <div class="col-sm-9">
          <select id='level' class='form-control form-control-sm'>
            <option class="level-1__" value="1">{{_("High")}}</option>
            <option class="level-12_" value="1,2">{{_("Normal or higher")}}</option>
            <option class="level-123" value="1,2,3">{{_("All")}}</option>
            <option disabled="disabled"></option>
            <option class="level-_2_" value="2">{{_("Normal only")}}</option>
            <option class="level-__3" value="3">{{_("Low only")}}</option>
          </select>
        </div>
      </div>
      <div id="fixable-span" class="form-group row">
        <label for='fixable' class="col-sm-3 col-form-label">{{_("Fixable")}}</label>
        <div class="col-sm-9">
          <select id="fixable" class="form-control form-control-sm" title="{{_("Show only markers with correction suggestions")}}">
            <option value=""></option>
            <option value="online">{{_("Online")}}</option>
            <option value="josm">JOSM</option>
          </select>
        </div>
      </div>
      <div id="tags-span" class="form-group row">
        <label for='tags' class="col-sm-3 col-form-label">{{_("Topic")}}</label>
        <div class="col-sm-9">
          <select id='tags' class='form-control form-control-sm'>
            <option value=""></option>
%for tag in tags:
            <option value="{{tag}}">{{_(tag)}}</option>
%end
          </select>
        </div>
      </div>
      {{_("Select:")}}
      <a href="#" class="toggleAllItem" data-view="all">{{_("all")}}</a>
      <a href="#" class="toggleAllItem" data-view="nothing">{{_("nothing")}}</a>
      <a href="#" class="invertAllItem">{{_("invert")}}</a>
    </div>
  <div id="tests" >
%it = set()
%for categ in categories:
    <div class="test_group" id="categ{{categ["categ"]}}">
    <h1><i class="toggleCategIco"></i><a href="#" class="toggleCateg">{{translate.select(categ["title"])}}</a>
    <span class="count">-/-</span>
    <a href="#" class="toggleAllItem" data-view="all">{{_("all")}}</a>
    <a href="#" class="toggleAllItem" data-view="nothing">{{_("nothing")}}</a></h1>
    <ul>
%    for err in categ["items"]:
%        it.add(err["item"])
        <li id='item_desc{{err["item"]}}' class="item" title="{{_("Item #%s") % err["item"]}}
%for classs in err["class"]:
{{classs["class"]}}. {{translate.select(classs["title"])}}
%end
"
>
            <div class="marker-l marker-l-{{err["item"]}}"></div>
            <div class="level">\\
%        ll = dict(map(lambda l: [l["level"], l["count"]], err["levels"]))
%        for i in [1,2,3]:
%            if i in ll:
<div class="level-{{i}}"><span>{{ll[i]}}</span></div>\\
%            else:
<div></div>\\
%            end
%        end
            </div>
            <input type='checkbox' id='item{{"{:04d}".format(err["item"])}}' name='item{{"{:04d}".format(err["item"])}}'/>
            <a target="_blank" href="../errors/?item={{err["item"]}}">{{translate.select(err["title"])}}</a>
        </li>
%    end
    </ul>
    </div>
%end
  </div>
</form>
</div>

<div id="doc">
<h5>{{_("Welcome to Osmose-QA")}}</h5>
<p>{{_("Osmose-QA a is quality assurance tools available to detect issues in OpenStreetMap data.")}}</p>
<p>{{_("It detects a very wide range of issue types. It is also useful for integrating third-party data sets or conflation.")}}</p>
<p>{{_("Feel free to report problem, idea or new OpenData you want to add to Osmose on our Github.")}}</p>
<p>{{_("In no case Osmose-QA should provide you the absolute right way to map, always keep a critical eye.")}}</p>
<p>{{_("You can find help on the wiki:")}} <a href="https://wiki.openstreetmap.org/wiki/Osmose" target="_blank">wiki.osm.org/Osmose</a></p>
</div>

<div id="map">
</div>

<div id='top_links'>
<ul id="topmenu">
<li id="menu-lang"><a href='#' onclick='return false;'>{{_("Change language")}} ▼</a>
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

<li id="menu-export"><a href='#' onclick='return false;'>{{_("Export")}} ▼</a>
<ul class="submenu">
  <li><a data-href="../errors/" target="_blank">{{_("Html list")}}</a></li>
  <li><a data-href="../josm_proxy?errors.josm" target="hiddenIframe">JOSM</a></li>
  <li><a data-href="../errors.rss" target="_blank">RSS</a></li>
  <li><a data-href="../errors.gpx">GPX</a></li>
  <li><a data-href="../errors.kml">KML</a></li>
  <li><a data-href="../api/0.3beta/issues" target="_blank">Json</a></li>
  <li><a data-href="../errors.csv" target="_blank">CSV</a></li>
  <li><a data-href="markers" target="_blank">GeoJson</a></li>
</ul>

<li id="menu-help"><a href='#' onclick='return false;'>{{_("Help")}} ▼</a>
<ul class="submenu">
%for u in helps:
 <li><a href="{{u[1]}}">{{u[0]}}</a></li>
%end
</ul>
</li>

%delay_status = "normal" if delay < 0.9 else "warning" if delay < 1.6 else "error"
%delay = "%0.2f" % delay
<li id="menu-delay"><a href="../control/update" class="delay-{{delay_status}}">{{_("Delay: %sd") % delay}}</a></li>

<li id="menu-user">
%if user:
  <a href="../byuser/{{user}}">{{user}} ({{user_error_count[1]+user_error_count[2]+user_error_count[3]}}) ▼</a>
  <ul class="submenu">
    <li><a href="../byuser/{{user}}?level=1">{{_("Level {level} issues ({count})") .format(level=1, count=user_error_count[1])}}</a></li>
    <li><a href="../byuser/{{user}}?level=2">{{_("Level {level} issues ({count})") .format(level=2, count=user_error_count[2])}}</a></li>
    <li><a href="../byuser/{{user}}?level=3">{{_("Level {level} issues ({count})") .format(level=3, count=user_error_count[3])}}</a></li>
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
  initMap();
});
</script>

<div id="editor" data-user="{{not not user}}"><p>{{_("You must be logged in order to use the tag editor")}}</p><a href="../login">{{_("Login")}}</a></div>

<div class="modal" id="dialog_editor_save_modal" data-backdrop="static" tabindex="-1" role="dialog" aria-hidden="true">
  <div class="modal-dialog modal-dialog-centered" role="document">
    <div class="modal-content">
      <div class="modal-header">
        <h5 class="modal-title">{{_("Save changeset")}}</h5>
      </div>
      <div class="modal-body" id="save_changeset">
        <form id="editor_save_form">
          <div class="form-group row">
            <label for="editor-modify-count" class="col-sm-4 col-form-label">{{_("Objects edited")}}</label>
            <div class="col-sm-8">
              <input type="text" readonly class="form-control-plaintext" id="editor-modify-count" value="">
            </div>
          </div>
          <div class="form-group row">
            <label for="editor-delete-count" class="col-sm-4 col-form-label">{{_("Objects deleted")}}</label>
            <div class="col-sm-8">
              <input type="text" readonly class="form-control-plaintext" id="editor-delete-count" value="">
            </div>
          </div>
          <div class="form-group row">
            <label for="comment" class="col-sm-4 col-form-label">{{_("Comment")}}</label>
            <div class="col-sm-8">
              <input class="form-control" type="text" name="comment" id="comment" value="{{_("Fix with Osmose")}}"/>
            </div>
          </div>
          <div class="form-group row">
            <label for="source" class="col-sm-4 col-form-label">{{_("Source")}}</label>
            <div class="col-sm-8">
              <input class="form-control" type="text" name="source" id="source" value=""/>
            </div>
          </div>
          <div class="form-group row">
            <label for="type" class="col-sm-4 col-form-label">{{_("Type")}}</label>
            <div class="col-sm-8">
              <input class="form-control" type="text" name="type" id="type" value="fix"/>
            </div>
          </div>
          <div class="form-group" row>
            <div class="col-sm-12">
              <input class="form-check-input" type="checkbox" name="reuse_changeset" id="reuse_changeset" checked="checked"/>
              <label class="form-check-label" for="reuse_changeset">{{_("Reuse changeset")}}</label>
            </div>
          </div>
        </form>
      </div>
      <div class="modal-body" id="save_uploading" style="display: none">
        <center><img src='../images/throbbler.gif' alt='downloading'></center>
      </div>
      <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-dismiss="modal">{{_("Cancel")}}</button>
        <button type="button" class="btn btn-primary" id="save_button">{{_("Save")}}</button>
      </div>
    </div>
  </div>
</div>

</body>
</html>
