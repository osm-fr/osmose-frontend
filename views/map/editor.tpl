{{!mustache_delimiter}}
<h1>{{_("Editor")}}</h1>
<%#elems%>
  <a target="_blank" href="http://www.openstreetmap.org/browse/<%type%>/<%id%>"><%type%> <%id%></a>
  <form>
    <div class="tags">
      <div class="del">
      </div>
      <div class="same">
      </div>
      <div class="mod">
      </div>
      <div class="add">
      </div>
    </div>
    <input type="button" id="validate" value="{{_("Ok")}}"/>
  </form>
<%/elems%>
