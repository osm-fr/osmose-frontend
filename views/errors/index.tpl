%rebase layout title=title
%import re
<a href=".?{{query}}">{{_("Informations")}}</a>
<a href="done?{{query}}">{{_("Fixed")}}</a>
<a href="false-positive?{{query}}">{{_("False positives")}}</a>
<a href="graph.png?{{query}}">{{_("Graph")}}</a>
<a href="../map/?{{query}}">{{_("Map")}}</a>
<br><br>

<form method='get' action=''>

<select name='country'>
    <option value=''></option>
%for res in countries:
%    if country == res['country']:
%        s = " selected='yes'"
%    else:
%        s = ""
%    end
    <option{{s}} value='{{res['country']}}'>{{res['country']}}</option>
%end
</select>

<select name='item'>
    <option value=''></option>
%for res in items:
%    if item == res['item']:
%        s = " selected='yes'"
%    else:
%        s = ""
%    end
    <option{{s}} value='{{res['item']}}'>{{res['item']}} - {{translate.select(res['menu'])}}</option>
%end
</select>

%# TRANSLATORS: 'Set' is used to choose a specific country/item on /errors
<input type='submit' value='{{_("Set")}}'>

</form>

<table class="sortable" id ="table_source">
<thead>
<tr>
    <th>#</th>
    <th>{{_("source")}}</th>
%# TRANSLATORS: this should be replaced by a abbreviation for class
    <th title="class">{{_("class (abbreviation)")}}</th>
    <th></th>
    <th class="sorttable_sorted">#<span id="sorttable_sortfwdindtable_source">&nbsp;▾</span></th>
    <th>{{_("item")}}</th>
    <th>{{_("title")}}</th>
    <th>{{_("count")}}</th>
</tr>
</thead>
<tbody>
%for res in errors_groups:
<tr>
    <td><a href="?source={{res["source"]}}">{{res["source"]}}</a></td>
%    cmt_split = res["source_comment"].split("-")
%    analyse = "-".join(cmt_split[0:-1])
%    country = cmt_split[-1]
    <td>{{analyse}}-<a href="?country={{country}}">{{country}}</a></td>
    <td><a href="?item={{res["item"]}}&amp;class={{res["class"]}}">{{res["class"]}}</a></td>
    <td title="{{res["item"]}}"><img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}"></td>
    <td><a href="?item={{res["item"]}}">{{res["item"]}}</a></td>
%    if res["menu"]:
    <td>{{translate.select(res["menu"])}}</td>
%    else:
    <td></td>
%    end
    <td>{{translate.select(res["title"])}}</td>
%    count = res["count"]
%    if count == -1:
%        count = "N/A"
%    end:
    <td><a href="?source={{res["source"]}}&amp;item={{res["item"]}}&amp;class={{res["class"]}}">{{count}}</a></td>
</tr>
%end
</tbody>
%if total > 0:
<tfoot>
<tr>
    <th colspan="7">{{_("Total")}}</th>
    <th style="text-align: left">{{total}}</th>
</tr>
</tfoot>
%end
</table>
<br>
%if errors:
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
%    if gen == "info":
    <th title="{{_("information on error")}}">E</th>
%    end
    <th title="{{_("position")}}">{{_("position (abbreviation)")}}</th>
    <th>{{_("elements (abbreviation)")}}</th>
%    if opt_date != "-1":
    <th>{{_("subtitle")}}</th>
%    else:
    <th class="sorttable_sorted">{{_("subtitle")}}<span id="sorttable_sortfwdind">&nbsp;▾</span></th>
%    end
%    if opt_date != "-1":
    <th class="sorttable_sorted">{{_("date")}}<span id="sorttable_sortfwdind">&nbsp;▾</span></th>
%    end
</tr>
</thead>
%    for res in errors:
<tr>
    <td title="{{res["source_comment"]}}"><a href="?source={{res["source"]}}">{{res["source"]}}</a></td>
    <td>{{res["class"]}}</td>
    <td>{{res["subclass"]}}</td>
    <td>{{res["level"]}}</td>
    <td title="{{res["item"]}}"><img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}"></td>
    <td><a href="?item={{res["item"]}}">{{res["item"]}}</a></td>
%        if res["menu"]:
    <td title="{{translate.select(res["title"])}}">{{translate.select(res["menu"])}}</td>
%        else:
    <td></td>
%        end
%        if gen == "info":
    <td title="erreur n°{{res["marker_id"]}}"><a href="../error/{{res["marker_id"]}}">E</a></td>
%        end
%        if res["lat"] and res["lon"]:
%            lat = res["lat"] / 1000000.
%            lon = res["lon"] / 1000000.
%            lat_s = "%.2f" % lat
%            lon_s = "%.2f" % lon
    <td><a href="/map/?zoom=13&amp;lat={{lat}}&amp;lon={{lon}}&amp;item={{res["item"]}}&amp;level={{res["level"]}}">{{lon_s}}&nbsp{{lat_s}}</a></td>
%        else:
    <td></td>
%        end
%        printed_td = False
%        if res["elems"]:
%            elems = res["elems"].split("_")
%            for e in elems:
%                m = re.match(r"([a-z]+)([0-9]+)", e)
%                if m:
%                    if not printed_td:
    <td sorttable_customkey="{{"%02d" % ord(m.group(1)[0])}}{{m.group(2)}}">
%                        printed_td = True
%                    else:
        &nbsp;
%                    end
%                    cur_type = m.group(1)
        {{cur_type[0]}}&nbsp;
        <a target="_blank" href="http://www.openstreetmap.org/browse/{{m.group(1)}}/{{m.group(2)}}">{{m.group(2)}}</a>&nbsp;
%                    if cur_type == "node":
%                        full_str = ""
%                    else:
%                        full_str = "/full"
%                    end
        &nbsp;<a title="josm" href="http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/{{m.group(1)}}/{{m.group(2)}}{{full_str}}" target="hiddenIframe">(j)</a>
%                end
%            end
%        end
%        if not printed_td:
%            minlat = lat - 0.002
%            maxlat = lat + 0.002
%            minlon = lon - 0.002
%            maxlon = lon + 0.002
    <td>
        <a href="http://localhost:8111/load_and_zoom?left={{minlon}}&amp;bottom={{minlat}}&amp;right={{maxlon}}&amp;top={{maxlat}}">josm</a>
    </td>
%        end
%        if res["subtitle"]:
    <td>{{translate.select(res["subtitle"])}}</td>
%        elif res["title"]:
    <td>{{translate.select(res["title"])}}</td>
%        else:
    <td></td>
%        end
%        if opt_date != "-1":
%            date = str(res["date"])
    <td>{{date[:10]}}&nbsp;{{date[11:16]}}</td>
%        end
</tr>
%    end
</table>
%    import urlparse, urllib
%    query_dict = urlparse.parse_qs(query)
%    points = int((query_dict.has_key("points") and query_dict["points"][0])) or 20
%    if points < total:
%        points *= 5
%    end
%    query_dict["points"] = points
<br>
<a href="?{{urllib.urlencode(query_dict, True)}}">{{_("Show more errors")}}</a>
%else:
<a href="?{{query}}&amp;points=100">{{_("Show some errors")}}</a>
%end
