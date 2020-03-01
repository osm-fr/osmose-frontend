%rebase('layout.tpl', title=_("Information on issue %s") % uuid, favicon="../images/markers/marker-l-%s.png" % marker['item'])
%def show_html_results(columns, res):
<table class="table table-striped table-bordered table-hover table-sm sortable" id="table_marker">
<thead class="thead-dark">
<tr>
    <th scope="col">{{_("key")}}</th>
    <th scope="col">{{_("value")}}</th>
</tr>
</thead>
<tbody>
%    i = 0
%    for c in columns:
%        c = c.split(" ")[-1]
<tr>
    <td>{{c}}</td>
    <td>
%        if type(res[i]) is dict:
            <table>
%            for (k, v) in res[i].items():
                <tr><td>{{k}}</td><td>{{v}}</td></tr>
%            end
            </table>
%        else:
{{res[i]}}
%        end
    </td>
</tr>
%        i += 1
%    end
</tbody>
</table>
%end

<h2>{{_("Marker")}}</h2>
%show_html_results(columns_marker, marker)
