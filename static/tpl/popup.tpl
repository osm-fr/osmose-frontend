<div id="popup-{{error_id}}">
  <div class="bulle_msg">
    <div class="closebubble">
      <div><a href="#" onclick="closeBubble('{{error_id}}');return false;"><b>&nbsp;X&nbsp;</b></a></div>
      <div class="help"><a target="_blank" href='{{url_help}}#{{item}}'>&nbsp;?&nbsp;</a></div>
      <div class="error-link"><a target="_blank" href="../error/{{error_id}}">&nbsp;E&nbsp;</a></div>
    </div>
    <div class="bulle_err">
      <b>{{title}}</b>
      <br>
      {{subtitle}}
      <br>
    </div>
{{#elems}}
    <div class="bulle_elem">
  {{^infos}}
      <b><a target="_blank" href="http://www.openstreetmap.org/browse/{{type}}/{{id}}">{{type}} {{id}}</a></b>
      <a href="javascript:iFrameLoad('http://rawedit.openstreetmap.fr/edit/{{type}}/{{id}}');">rawedit</a>
  {{/infos}}
  {{#relation}}
      <a target="_blank" href="http://analyser.openstreetmap.fr/cgi-bin/index.py?relation={{id}}">analyse1</a>
      <a target="_blank" href="http://osm3.crans.org/osmbin/analyse-relation?{{id}}">analyse2</a>
  {{/relation}}
  {{#node}}
      <a href="http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/node/{{id}}" target="hiddenIframe">josm</a>
  {{/node}}
  {{#way}}
      <a href="http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/{{type}}/{{id}}/full" target="hiddenIframe">josm</a>
  {{/way}}
  {{#relation}}
      <a href="http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/{{type}}/{{id}}/full" target="hiddenIframe">josm</a>
  {{/relation}}
      <br>
  {{#fixes}}
      <div class="fix">
        <a class="link" href="http://localhost:8111/import?url=http://{{website}}/error/{{error_id}}/fix/{{num}}" target="hiddenIframe">josm fix</a>
    {{#add}}
        <div class="add"> + <b>{{k}}</b> = {{v}}</div>
    {{/add}}
    {{#mod}}
        <div class="mod"> ~ <b>{{k}}</b> = {{v}}</div>
    {{/mod}}
    {{#del}}
        <div class="del"> - <b>{{k}}</b></div>
    {{/del}}
      </div>
  {{/fixes}}
  {{#tags}}
      <b>{{k}}</b> = {{v}}<br>
  {{/tags}}
    </div>
{{/elems}}
{{#new_elems}}
    <div class="bulle_elem">
      <div class="fix">
        <a class="link" href="http://localhost:8111/import?url=http://{{website}}/error/{{error_id}}/fix/{{num}}" target="hiddenIframe">josm fix</a>
  {{#add}}
        <div class="add"> + <b>{{k}}</b> = {{v}}</div>
  {{/add}}
  {{#mod}}
        <div class="mod"> ~ <b>{{k}}</b> = {{v}}</div>
  {{/mod}}
  {{#del}}
        <div class="del"> - <b>{{k}}</b></div>
  {{/del}}
      </div>
    </div>
{{/new_elems}}
_("Error reported on: ") {{b_date}}
  </div>
  <div class="bulle_verif">
    <a href="http://www.openstreetmap.org/?lat={{lat}}&lon={{lon}}&zoom=18" target="_blank">osmlink</a>
    <a href="http://www.openstreetmap.org/edit?lat={{lat}}&lon={{lon}}&zoom=18" target="_blank">potlatch</a>
    <a href="http://localhost:8111/load_and_zoom?left={{minlon}}&bottom={{minlat}}&right={{maxlon}}&top={{maxlat}}&select={{elems_id}}" target="hiddenIframe">josm zone</a>
  </div>
  <div class="bulle_maj">
    <b>_("change status") :</b>
    <a onclick="setTimeout('pois.loadText();',2000);" href="../error/{{error_id}}/done" target="hiddenIframe">_("corrected")</a>
    <a onclick="setTimeout('pois.loadText();',2000);" href="../error/{{error_id}}/false" target="hiddenIframe">_("false positive")</a>
</div>

</div>
