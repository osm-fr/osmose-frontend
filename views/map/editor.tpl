{{!mustache_delimiter}}
<h1>{{_("Tags Editor")}}</h1>
<form>
  <%#elems%>
  <a target="_blank" href="http://www.openstreetmap.org/browse/<%type%>/<%id%>"><%type%> <%id%></a>
  <div class="tags" data-type="<%type%>" data-id="<%id%>" data-version="<%version%>">
    <div class="del">
    </div>
    <div class="same">
    </div>
    <div class="mod">
    </div>
    <div class="add">
    </div>
  </div>
  <%/elems%>
  </br>
  <div id="buttons">
    <input type="button" id="cancel" value="{{_("Cancel")}}"/>
    <input type="button" id="validate" value="{{_("Ok")}}"/>
  </div>
</form>
