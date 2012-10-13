%rebase layout title=_("Last updates")
<table>
<tr bgcolor="#999999">
    <th width="50">{{_("source")}}</th>
    <th width="600">{{_("description")}}</th>
    <th width="200">{{_("last generation")}}</th>
    <th width="30">{{_("history")}}</th>
</tr>
%odd = True
%for source in liste:
%    odd = not odd
%    if odd:
    <tr bgcolor="#BBBBBB">
%    else:
    <tr bgcolor="#EEEEEE">
%    end
    <td><a href="../errors/?source={{source[3]}}">{{source[3]}}</a></td>
    <td>{{source[0]}}</td>
    <td>{{source[2]}}</td>
    <td><a href="update/{{source[3]}}">{{_("history")}}</a></td>
    </tr>
%end
</table>
