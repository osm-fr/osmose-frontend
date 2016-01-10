{{!mustache_delimiter}}
<div id="popup-{%error_id%}">
  <div class="bulle_msg">
    <div class="closebubble">
      <div class="help"><a target="_blank" href='{%url_help%}#{%item%}'>&nbsp;?&nbsp;</a></div>
      <div class="error-link"><a target="_blank" href="../error/{%error_id%}">&nbsp;E&nbsp;</a></div>
    </div>
    <div class="bulle_err">
      <b>{% title %}</b>
      <br>
      {%subtitle%}
    </div>
{%#elems%}
    <div class="bulle_elem">
  {%^infos%}
      <b><a target="_blank" href="{{main_website}}browse/{%type%}/{%id%}">{%type%} {%id%}</a></b>
      <a href="#" onclick="window.open('http://rawedit.openstreetmap.fr/edit/{%type%}/{%id%}','rawedit','height=360,width=710');">rawedit</a>
  {%/infos%}
  {%#relation%}
      <a target="_blank" href="http://analyser.openstreetmap.fr/cgi-bin/index.py?relation={%id%}">analyse1</a>
      <a target="_blank" href="http://polygons.openstreetmap.fr/~osmbin/analyse-relation-open.py?{%id%}">analyse2</a>
  {%/relation%}
  {%#node%}
      <a href="http://localhost:8111/load_object?objects=n{%id%}" target="hiddenIframe" class="josm">josm</a>
  {%/node%}
  {%#way%}
      <a href="http://localhost:8111/load_object?objects=w{%id%}" target="hiddenIframe" class="josm">josm</a>
  {%/way%}
  {%#relation%}
      <a href="http://localhost:8111/import?url={{remote_url_read}}api/0.6/{%type%}/{%id%}/full" target="hiddenIframe" class="josm">josm</a>
  {%/relation%}
      <a href="#" class="editor_edit" data-type="{%type%}" data-id="{%id%}" data-error="{%error_id%}">edit</a>
      <br>
  {%#fixes%}
      <div class="fix">
        <div class="fix_links">
            <a href="http://localhost:8111/import?url=http://{{website}}/api/0.2/error/{%error_id%}/fix/{%num%}" target="hiddenIframe" class="josm">fix-josm</a>
            <a href="#" class="editor_fix" data-type="{%type%}" data-id="{%id%}" data-error="{%error_id%}" data-fix="{%num%}">fix-edit</a>
        </div>
    {%#add%}
        <div class="add"> + <b>{%k%}</b> = {%v%}</div>
    {%/add%}
    {%#mod%}
        <div class="mod"> ~ <b>{%k%}</b> = {%v%}</div>
    {%/mod%}
    {%#del%}
        <div class="del"> - <b>{%k%}</b></div>
    {%/del%}
      </div>
  {%/fixes%}
  {%#tags%}
      <b>{%k%}</b> =
      {%#vlink%}<a href="{%vlink%}" target="_blank">{%/vlink%}
      {%v%}
      {%#vlink%}</a>{%/vlink%}
      <br>
  {%/tags%}
    </div>
{%/elems%}
{%#new_elems%}
    <div class="bulle_elem">
      <div class="fix">
        <div class="fix_links">
          <a href="http://localhost:8111/import?url=http://{{website}}/api/0.2/error/{%error_id%}/fix/{%num%}" target="hiddenIframe" class="josm">fix-josm</a>
        </div>
  {%#add%}
        <div class="add"> + <b>{%k%}</b> = {%v%}</div>
  {%/add%}
  {%#mod%}
        <div class="mod"> ~ <b>{%k%}</b> = {%v%}</div>
  {%/mod%}
  {%#del%}
        <div class="del"> - <b>{%k%}</b></div>
  {%/del%}
      </div>
    </div>
{%/new_elems%}
{{_("Issue reported on: ")}} {%b_date%}
  </div>
  <div class="bulle_verif">
    <a href="{{main_website}}?lat={%lat%}&lon={%lon%}&zoom=18" target="_blank">osm-show</a>
    <a href="{{main_website}}edit?lat={%lat%}&lon={%lon%}&zoom=18" target="_blank">osm-edit</a>
    <a href="http://localhost:8111/load_and_zoom?left={%minlon%}&bottom={%minlat%}&right={%maxlon%}&top={%maxlat%}&select={%elems_id%}" target="hiddenIframe" class="josm">josm zone</a>
  </div>
  <div class="bulle_maj">
    <b>{{_("change status")}} :</b>
    <a class="closePopup corrected" href="../api/0.2/error/{%error_id%}/done" target="hiddenIframe">{{_("corrected")}}</a>
    <a class="closePopup false_positive" href="../api/0.2/error/{%error_id%}/false" target="hiddenIframe">{{_("false positive")}}</a>
</div>

</div>
