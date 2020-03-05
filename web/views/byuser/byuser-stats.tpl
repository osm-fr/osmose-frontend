%rebase('layout.tpl', title=_("Users statistics"))
<table class="table table-striped table-bordered table-hover table-sm">
<thead class="thead-dark">
  <tr>
    <th scope="col">#</th>
    <th scope="col">{{_("Number")}}</th>
    <th scope="col">{{_("Username")}}</th>
  </tr>
</thead>
<tbody>
%i = 1
%for res in results:
  <tr>
    <td>{{i}}</td>
    <td>{{res["count"]}}</td>
    <td><a href="byuser/{{res["username"]}}">{{res["username"]}}</a></td>
  </tr>
%    i += 1
%end
</tbody>
</table>
