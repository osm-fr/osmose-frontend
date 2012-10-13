%rebase layout title=_("Update")
  <style type="text/css">
  table
  {
    border-width: 1px 1px 1px 1px;
    border-style: solid;
    border-collapse: collapse;
  }
  td
  {
    border-width: 1px 1px 1px 1px;
    border-style: solid;
    margin: 0px;
    padding: 5px;
  }
  a:link {
    color: black;
  }
    a:visited {
    color: black;
  }
    a:hover {
    color: black;
  }
  </style>

<table>
<tr bgcolor="#999999">
    <th width="50">{{_("source")}}</td>
    <th width="800">{{_("remote url")}}</td>
    <th width="200">{{_("timestamp")}}</td>
</tr>
%odd = True
%for res in liste:
%    odd = not odd
%    if odd:
    <tr bgcolor="#BBBBBB">
%    else:
    <tr bgcolor="#EEEEEE">
%     end
    <td><a href="../../errors?source={{res[0]}}">{{res[0]}}</a></td>
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
