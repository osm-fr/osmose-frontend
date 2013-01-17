%rebase layout title=_("Update")
<table>
<tr>
    <th>{{_("source")}}</td>
    <th style="min-width: 800px">{{_("remote url")}}</td>
    <th>{{_("timestamp")}}</td>
</tr>
%for res in liste:
<tr>
    <td><a href="../../errors/?source={{res[0]}}">{{res[0]}}</a></td>
%    url = res[2]
%    url = url.replace("http://cedric.dumez-viou.fr", "http://cdv")
%    url = url.replace("http://osm1.crans.org", "http://osm1")
%    url = url.replace("http://osm2.crans.org", "http://osm2")
%    url = url.replace("http://osm3.crans.org", "http://osm3")
%    url = url.replace("http://osm4.crans.org", "http://osm4")
%    url = url.replace("http://osm5.univ-nantes.fr", "http://osm5")
%    url = url.replace("http://osm6.univ-nantes.fr", "http://osm6")
%    url = url.replace("http://osm7.pole-aquinetic.fr", "http://osm7")
%    url = url.replace("http://osm8.pole-aquinetic.fr", "http://osm8")
    <td>{{url}}</td>
    <td>{{res[1]}}</td>
</tr>
%end
</table>
