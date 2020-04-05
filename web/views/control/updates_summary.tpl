%rebase('layout.tpl', title=_("Updates summary"))
%def col(tag, age, count):
%            if age > 2.05:
    <{{tag}} style="background-color: rgba(255, 0, 0, {{count}});">\\
%            elif age > 1.05:
    <{{tag}} style="background-color: rgba(255, 127, 0, {{count}});">\\
%            else:
    <{{tag}}>\\
%            end

%end
<table class="table table-striped table-bordered table-hover table-sm sortable">
%for remote in sorted(summary.keys(), key=lambda remote: hostnames[remote] or ''):
<thead class="thead-dark">
<tr><th>{{hostnames[remote] or remote}} <a href="update_matrix?remote={{remote_hashes[remote]}}">{{remote_hashes[remote]}}</a> ({{min_versions[remote]}} - {{max_versions[remote]}})</th></tr>
</thead>
<tbody>
<tr><td>
%    for country in summary[remote]:
%        opacity = 0.66*country['count']/max_count+0.33
%        col('span', country['min_age'], opacity)
<a href="../errors/?country={{country['country']}}&item=xxxx">{{country['country']}}</a><sup>{{country['count']}}</sup>
%        col('span', country['max_age'], opacity)
{{"%0.1f" % country['max_age']}}</span>-{{"%0.1f" % country['min_age']}}</span>
</span>&nbsp;
%    end
</td></tr>
</tbody>
%end
</table>
