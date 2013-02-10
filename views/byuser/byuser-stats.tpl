%rebase layout title=_("Users statistics")
<table>
  <tr>
    <th>#</th>
    <th>{{_("Number")}}</th>
    <th>{{_("Username")}}</th>
  </tr>
%i = 1
%for res in results:
  <tr>
    <td>{{i}}</td>
    <td>{{res["count"]}}</td>
    <td><a href="byuser/{{res["username"]}}">{{res["username"]}}</a></td>
  </tr>
%    i += 1
%end
</table>
