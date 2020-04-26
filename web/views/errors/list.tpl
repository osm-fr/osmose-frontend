%import re
<table class="table table-striped table-bordered table-hover table-sm sortable">
<thead class="thead-dark">
<tr>
    <th scope="col" title="source">{{_("source")}}</th>
%# TRANSLATORS: this should be replaced by a abbreviation for level
    <th scope="col" title="level">{{_("level (abbreviation)")}}</th>
    <th scope="col">{{_("item")}}</th>
%# TRANSLATORS: this should be replaced by a abbreviation for class
    <th scope="col" title="class">{{_("class (abbreviation)")}}</th>
    <th scope="col" title="{{_("information on issue")}}">E</th>
    <th scope="col" title="{{_("position")}}">{{_("position (abbreviation)")}}</th>
    <th scope="col">{{_("elements (abbreviation)")}}</th>
    <th scope="col">{{_("subtitle")}}</th>
%if opt_date != "-1":
    <th scope="col">{{_("date")}}</th>
%end
%if gen in ("error", "info"):
    <th title="{{_("False positive / Done")}}">✘/✔</th>
%end
%if gen == "false-positive":
    <th title="{{_("delete issue")}}">✘</th>
%end
</tr>
</thead>
%for res in errors:
<tr>
    <td title="{{res["country"] + "-" + res["analyser"]}}"><a href="?{{!page_args}}source={{res["source"]}}">{{res["source"]}}</a></td>
    <td>{{res["level"]}}</td>
    <td>
        <img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}">
        <a href="?{{!page_args}}item={{res["item"]}}">{{res["item"]}}</a>
%        if res["menu"]:
            {{translate.select(res["menu"])}}
%        end
    </td>
    <td>{{res["class"]}}</td>
%    e = gen if gen in ('error', 'false-positive') else 'error'
    <td title="{{_(u"issue n°")}}{{res["uuid"]}}"><a href="../{{e}}/{{res["uuid"]}}">E</a></td>
%    if res["lat"] and res["lon"]:
%        lat = res["lat"]
%        lon = res["lon"]
%        lat_s = "%.2f" % lat
%        lon_s = "%.2f" % lon
    <td><a href="/map/#{{query}}&amp;item={{res["item"]}}&amp;zoom=17&amp;lat={{lat}}&amp;lon={{lon}}&amp;level={{res["level"]}}&tags=&fixable=">{{lon_s}}&nbsp;{{lat_s}}</a></td>
%    else:
    <td></td>
%    end
%    printed_td = False
%    if res["elems"]:
%        for e in res["elems"]:
%                if not printed_td:
    <td sorttable_customkey="{{"%02d" % ord(e['type'])}}{{e['id']}}">
%                    printed_td = True
%                else:
        &nbsp;
%                end
        {{e['type'].lower()}}&nbsp;
        <a target="_blank" href="{{main_website}}{{e['type_long']}}/{{e['id']}}">{{e['id']}}</a>&nbsp;
        &nbsp;
%                if e['type'] == "R":
        <a title="josm" href="../josm_proxy?import?url={{remote_url_read}}/api/0.6/relation/{{e['id']}}/full" target="hiddenIframe" onclick="$.get('http://localhost:8111/zoom?left={%minlon%}&bottom={%minlat%}&right={%maxlon%}&top={%maxlat%}'); return true;">(j)</a>
%                else:
        <a title="josm" href="../josm_proxy?load_object?objects={{e['type'].lower()}}{{e['id']}}" target="hiddenIframe">(j)</a>
%                end
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
%    if gen in ("error", "info"):
    <td>
      <a href="#" class="err_delete" id="GET=issue/{{res["uuid"]}}/false" title="{{_("Mark issue #%s as false positive") % res["uuid"]}}">✘</a>/
      <a href="#" class="err_delete" id="GET=issue/{{res["uuid"]}}/done" title="{{_("Mark issue #%s as fixed") % res["uuid"]}}">✔</a>
    </td>
%    end
%    if gen == "false-positive":
    <td title="{{_("delete issue #%s") % res["uuid"]}}"><a href="#" class="err_delete" id="DELETE={{gen}}/{{res["uuid"]}}">✘</a></td>
%    end
</tr>
%end
</table>
<iframe id="hiddenIframe" name="hiddenIframe"></iframe>
