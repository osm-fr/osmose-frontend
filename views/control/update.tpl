%rebase('layout.tpl', title=_("Update"))
<table class="table table-striped table-bordered table-hover table-sm sortable">
<thead class="thead-dark">
<tr>
    <th>{{_("source")}}</td>
    <th style="min-width: 800px">{{_("remote url")}}</td>
    <th>{{_("timestamp")}}</td>
    <th>{{_("version")}}</td>
</tr>
</thead>
<tbody>
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
    <td>{{res[4]}}</td>
</tr>
%end
</tbody>
</table>
