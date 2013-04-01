%import re
<table class="sortable">
<thead>
<tr>
    <th title="source">{{_("source")}}</th>
%# TRANSLATORS: this should be replaced by a abbreviation for class
    <th title="class">{{_("class (abbreviation)")}}</th>
%# TRANSLATORS: this should be replaced by a abbreviation for subclass
    <th title="subclass">{{_("subclass (abbreviation)")}}</th>
%# TRANSLATORS: this should be replaced by a abbreviation for subclass
    <th title="level">{{_("level (abbreviation)")}}</th>
    <th></th>
    <th>#</th>
    <th>{{_("item")}}</th>
%if gen == "info":
    <th title="{{_("information on error")}}">E</th>
%end
    <th title="{{_("position")}}">{{_("position (abbreviation)")}}</th>
    <th>{{_("elements (abbreviation)")}}</th>
    <th>{{_("subtitle")}}</th>
%if opt_date != "-1":
    <th>{{_("date")}}</th>
%end
</tr>
</thead>
%for res in errors:
<tr>
    <td title="{{res["comment"]}}"><a href="?source={{res["source"]}}">{{res["source"]}}</a></td>
    <td>{{res["class"]}}</td>
    <td>{{res["subclass"]}}</td>
    <td>{{res["level"]}}</td>
    <td title="{{res["item"]}}"><img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}"></td>
    <td><a href="?item={{res["item"]}}">{{res["item"]}}</a></td>
%    if res["menu"]:
    <td title="{{translate.select(res["title"])}}">{{translate.select(res["menu"])}}</td>
%    else:
    <td></td>
%    end
%    if gen == "info":
    <td title="erreur n°{{res["id"]}}"><a href="../error/{{res["id"]}}">E</a></td>
%    end
%    if res["lat"] and res["lon"]:
%        lat = res["lat"]
%        lon = res["lon"]
%        lat_s = "%.2f" % lat
%        lon_s = "%.2f" % lon
    <td><a href="/map/?zoom=13&amp;lat={{lat}}&amp;lon={{lon}}&amp;item={{res["item"]}}&amp;level={{res["level"]}}">{{lon_s}}&nbsp;{{lat_s}}</a></td>
%    else:
    <td></td>
%    end
%    printed_td = False
%    if res["elems"]:
%        elems = res["elems"].split("_")
%        for e in elems:
%            m = re.match(r"([a-z]+)([0-9]+)", e)
%            if m:
%                if not printed_td:
    <td sorttable_customkey="{{"%02d" % ord(m.group(1)[0])}}{{m.group(2)}}">
%                    printed_td = True
%                else:
        &nbsp;
%                end
%                cur_type = m.group(1)
        {{cur_type[0]}}&nbsp;
        <a target="_blank" href="http://www.openstreetmap.org/browse/{{m.group(1)}}/{{m.group(2)}}">{{m.group(2)}}</a>&nbsp;
        &nbsp;
%                if cur_type == "relation":
        <a title="josm" href="http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/relation/{{m.group(2)}}/full" target="hiddenIframe">(j)</a>
%                else:
        <a title="josm" href="http://localhost:8111/load_object?objects={{cur_type[0]}}{{m.group(2)}}" target="hiddenIframe">(j)</a>
%                end
%            end
%        end
%    end
%    if not printed_td:
%        minlat = float(lat) - 0.002
%        maxlat = float(lat) + 0.002
%        minlon = float(lon) - 0.002
%        maxlon = float(lon) + 0.002
    <td>
        <a href="http://localhost:8111/load_and_zoom?left={{minlon}}&amp;bottom={{minlat}}&amp;right={{maxlon}}&amp;top={{maxlat}}">josm</a>
    </td>
%    end
%    if res["subtitle"]:
    <td>{{translate.select(res["subtitle"])}}</td>
%    elif res["title"]:
    <td>{{translate.select(res["title"])}}</td>
%    else:
    <td></td>
%    end
%    if opt_date != "-1":
%        date = str(res["date"])
    <td>{{date[:10]}}&nbsp;{{date[11:16]}}</td>
%    end
</tr>
%end
</table>
<iframe id="hiddenIframe" name="hiddenIframe"></iframe>
