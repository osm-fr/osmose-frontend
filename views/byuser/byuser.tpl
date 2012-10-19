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
    <th></th>
    <th>{{_("item")}}</th>
    <th>{{_("class (abbreviation)")}}<span id="sorttable_sortfwdind">&nbsp;▾</span></th>
    <th>{{_("level (abbreviation)")}}</th>
    <th>{{_("Title")}}</th>
    <th>{{_("Error")}}</th>
    <th title="{{_("information on error")}}">E</th>
    <th>josm</th>
    <th title="{{_("position")}}">{{_("position (abbreviation)")}}</th>
  </tr>

%for res in results:
  <tr>
    <td title="{{res["item"]}}"><img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}"></td>
    <td>{{res["item"]}}</td>
    <td>{{res["class"]}}</td>
    <td>{{res["level"]}}</td>
    <td>{{translate.select(res["title"])}}</td>
    <td>
%    if res["subtitle"]:
        {{translate.select(res["subtitle"])}}
%    end
    </td>
    <td title="erreur n°{{res["id"]}}"><a href="../error/{{res["id"]}}">E</a></td>
%    lat = float(res["lat"])/1000000.
%    lon = float(res["lon"])/1000000.
%    minlat = lat - 0.002
%    maxlat = lat + 0.002
%    minlon = lon - 0.002
%    maxlon = lon + 0.002
    <td><a href="http://localhost:8111/load_and_zoom?left={{minlon}}&amp;bottom={{minlat}}&amp;right={{maxlon}}&amp;top={{maxlat}}">josm</a></td>
%    cl = res["class"]
%    source = res["source"]
%    item = res["item"]
%    level = res["level"]
%    lat_s = "%.2f" % lat
%    lon_s = "%.2f" % lon
    <td><a href='/map/?zoom=16&amp;lat={{lat}}&amp;lon={{lon}}&amp;item={{item}}&amp;level={{level}}'>{{lon_s}}&nbsp{{lat_s}}</a></td>
  </tr>
%end
</table>
