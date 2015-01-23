%rebase('layout.tpl', title=_("Update"))
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
%    if url.startswith("http://"):
%      url = url.split("/")[2]
%    elif res[3]:
%      url = res[3]
%    end
    <td>{{url}}</td>
    <td>{{res[1]}}</td>
</tr>
%end
</table>
