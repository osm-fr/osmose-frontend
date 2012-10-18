%rebase layout title=_("Information on error %d") % err_id
%def show_html_results(columns, res):
<table class="sortable" id ="table_marker">
<thead>
<tr>
    <th>{{_("key")}}</th>
    <th>{{_("value")}}</th>
</tr>
</thead>
%    i = 0
%    for c in columns:
%        c = c.split(".")[-1]
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
</table>
%end

<h2>{{_("Marker")}}</h2>
%for i in marker:
%    show_html_results(columns_marker, i)
%end

<h2>{{_("Elements")}}</h2>
%for i in elements:
%    show_html_results(columns_elements, i)
%end

<h2>{{_("Fixes")}}</h2>
%for i in fix:
%    show_html_results(columns_fix, i)
%end
