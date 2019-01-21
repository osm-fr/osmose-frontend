%rebase('layout.tpl', title=_("Updates summary"))
%def col(t, v):
%  if v > 2.05:
<{{t}} class="delay-error">\\
%  elif v > 1.05:
<{{t}} class="delay-warning">\\
%  else:
<{{t}}>\\
%  end
%end

%def col_version(t, max, v):
%  if v != '' and v != max:
<{{t}} class="delay-warning">\\
%  else:
<{{t}}>\\
%  end
%end

<table class="table table-striped table-bordered table-hover table-sm sortable">
<thead class="thead-dark">
<tr><th>{{_('Analyser')}}</th><th>{{_('Count')}}</th><th>{{_('Age')}}</th><th>{{_('Version')}}</th></tr>
</thead>
<tbody>
%for analyser in sorted(summary.keys()):
<tr>
  <td>{{analyser}}</td>
  <td>{{summary[analyser]['count']}}</td>
  <td>\\
%col('span', summary[analyser]['min_age'])
{{"%0.1f" % summary[analyser]['min_age']}}-\\
%col('span', summary[analyser]['max_age'])
{{"%0.1f" % summary[analyser]['max_age']}}</span></span></td>
  <td>\\
%col_version('span', max_versions, summary[analyser]['min_version'])
{{summary[analyser]['min_version']}}</span>
 - \\
%col_version('span', max_versions, summary[analyser]['max_version'])
{{summary[analyser]['max_version']}}</span></td>
</tr>
%end
</tbody>
</table>
