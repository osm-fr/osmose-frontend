%rebase('layout.tpl', title=_("Last updates"))
<p>{{_("Median delay:")}} {{(liste[len(liste)/2][2]) if len(liste)>0 else ""}}</p>
<table>
<tr>
    <th>{{_("source")}}</th>
    <th style="min-width: 100px">{{_("country")}}</th>
    <th style="min-width: 100px">{{_("analyser")}}</th>
    <th style="min-width: 200px">{{_("last generation")}}</th>
    <th>{{_("history")}}</th>
</tr>
%for source in liste:
<tr>
    <td><a href="../errors/?source={{source[4]}}">{{source[4]}}</a></td>
    <td>{{source[0]}}</td>
    <td>{{source[1]}}</td>
    <td>{{source[3]}}</td>
    <td><a href="update/{{source[4]}}">{{_("history")}}</a></td>
</tr>
%end
</table>
