%rebase('layout.tpl', title=_("Updates summary"))
%def col(t, v):
%            if v > 4.05:
    <{{t}} class="delay-error">\\
%            elif v > 2.05:
    <{{t}} class="delay-warning">\\
%            else:
    <{{t}}>\\
%            end

%end
<table>
%for remote in summary.keys():
<tr><th><a href="update_matrix?remote={{remote_hashes[remote]}}">{{remote}}</a> ({{min_versions[remote]}} - {{max_versions[remote]}})</th></tr>
<tr><td>
%    for country in summary[remote]:
%        col('span', country['min_age'])
<a href="../errors/?country={{country['country']}}&item=xxxx">{{country['country']}}</a><sup>{{country['count']}}</sup>
%        col('span', country['max_age'])
{{"%0.1f" % country['max_age']}}</span>-{{"%0.1f" % country['min_age']}}</span>
</span>&nbsp;⚫
%    end
</td></tr>
%end
</table>
