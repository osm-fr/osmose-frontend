%rebase layout title=(_("Statistics for user %s") % username)
<h1>{{_("User statistics for %s") % username}}</h1>
<p>{{_("This page shows errors on elements that were last modified by '%s'. This doesn't means that this user is responsible for all these errors.") % username}}</p>
<p>
%if count < 500:
    {{_("Number of found errors: %d") % count}}
%else:
    {{_("Number of found errors: more than %d") % count}}
%end
 - 
<a href='/map/?user={{username}}'>{{_("Show errors on a map")}}</a>
</p>

<table class='sortable'>
  <tr>
    <th>{{_("Item")}}</th>
    <th>{{_("Class")}}<span id="sorttable_sortfwdind">&nbsp;▾</span></th>
    <th>{{_("Level")}}</th>
    <th>{{_("Title")}}</th>
    <th>{{_("Error")}}</th>
    <th>{{_("Latitude")}}</th>
    <th>{{_("Longitude")}}</th>
    <th></th>
  </tr>

%for res in results:
  <tr>
    <td>{{res["item"]}}</td>
    <td>{{res["class"]}}</td>
    <td>{{res["level"]}}</td>
    <td>{{translate.select(res["title"])}}</td>
    <td>
%    if res["subtitle"]:
        {{translate.select(res["subtitle"])}}
%    end
    </td>
%    lat = str(float(res["lat"])/1000000)
%    lon = str(float(res["lon"])/1000000)
%    cl = res["class"]
%    source = res["source"]
%    item = res["item"]
%    level = res["level"]
    <td>{{lat}}</td>
    <td>{{lon}}</td>
    <td><a href='/map/?zoom=16&amp;lat={{lat}}&amp;lon={{lon}}&amp;item={{item}}&amp;level={{level}}'>{{_("map")}}</a></td>
  </tr>
%end
</table>
