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
%for e in elems:
<div class="bulle_elem">
%    if e[0] != "infos":
    <b><a target="_blank" href="http://www.openstreetmap.org/browse/{{e[0]}}/{{e[1]}}">{{e[0]}} {{e[1]}}</a></b>
    <a href="javascript:iFrameLoad('http://rawedit.openstreetmap.fr/edit/{{e[0]}}/{{e[1]}}');">rawedit</a>
%    end
%    if e[0] == "relation" and "boundary" in e[2]:
    <a target="_blank" href="http://analyser.openstreetmap.fr/cgi-bin/index.py?relation={{e[1]}}">analyse1</a>
    <a target="_blank" href="http://osm3.crans.org/osmbin/analyse-relation?{{e[1]}}">analyse2</a>
%    end
%    if e[0] == "node":
    <a href="http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/node/{{e[1]}}" target="hiddenIframe">josm</a>
%    end
%    if e[0] == "way" or e[0] == "relation":
    <a href="http://localhost:8111/import?url=http://www.openstreetmap.org/api/0.6/{{e[0]}}/{{e[1]}}/full" target="hiddenIframe">josm</a>
%    end
    <br>
%    for i in xrange(3, len(e)):
    <div class="fix">
        <a class="link" href="http://localhost:8111/import?url=http://{{utils.website}}/error/{{error_id}}/fix/{{e[i][3]}}" target="hiddenIframe">josm fix</a>
%        for (k, v) in e[i][0].items():
        <div class="add"> + <b>{{k}}</b> = {{v}}<br></div>
%        end
%        for (k, v) in e[i][1].items():
        <div class="mod"> ~ <b>{{k}}</b> = {{v}}<br></div>
%        end
%        for k in e[i][2]:
        <div class="del"> - <b>{{k}}</b></div>
%        end
    </div>"
%    end
%    for t in e[2].items():
    <b>{{t[0]}}</b> = {{t[1]}}<br>
%    end
</div>
%end
%for e in new_elems:
<div class="bulle_elem">
    <div class="fix">"
    <a class="link" href="http://localhost:8111/import?url=http://{{utils.website}}/error/{{error_id}}/fix/{{e[3]}}" target="hiddenIframe">josm fix</a>
%    for (k, v) in e[0].items():
    <div class="add"> + <b>{{k}}</b> = {{v}}<br></div>
%    end
%    for (k, v) in e[1].items():
    <div class="mod"> ~ <b>{{k}}</b> = {{v}}<br></div>
%    end
%    for k in e[2]:
    <div class="del"> - <b>{{k}}</b></div>
%    end
    </div>
</div>
%end
{{_("Error reported on: ")}} {{b_date.strftime("%Y-%m-%d")}}
</div>
<div class="bulle_verif">
<a href="http://www.openstreetmap.org/?lat={{lat}}&lon={{lon}}&zoom=18" target="_blank">osmlink</a>
<a href="http://www.openstreetmap.org/edit?lat={{lat}}&lon={{lon}}&zoom=18" target="_blank">potlatch</a>
%minlat = float(lat) - 0.002
%maxlat = float(lat) + 0.002
%minlon = float(lon) - 0.002
%maxlon = float(lon) + 0.002
<a href="http://localhost:8111/load_and_zoom?left={{minlon}}&bottom={{minlat}}&right={{maxlon}}&top={{maxlat}}"\\
if reselems:
&select={{reselems.replace("_",",")}}\\
" target="hiddenIframe">josm zone</a>
</div>
<div class="bulle_maj">
<b>{{_("change status")}} :</b>
<a onclick="setTimeout('pois.loadText();',2000);" href="../error/{{error_id}}/done" target="hiddenIframe">{{ _("corrected")}}</a>
<a onclick="setTimeout('pois.loadText();',2000);" href="../error/{{error_id}}/false" target="hiddenIframe">{{_("false positive")}}</a>
</div>
