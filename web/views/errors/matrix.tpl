%rebase('layout.tpl', title=_("Issue counts matrix"))
%def n(m):
%  return '{:,}'.format(m).replace(',', ' ')
%end
<style>
th.n, td {
  text-align: right;
  font-size: 80%;
}
</style>
<div style="font-size:50%">
<table class="table table-striped table-bordered table-hover table-sm sortable">
<thead>
<tr>
    <th class="n" colspan="2" rowspan="2">{{n(total)}}</th>
%countries = sorted(countries_sum.items(), key=lambda k: -k[1])
%for country, sum in countries:
    <th class="country"><div class="rotate-90"><a href="../errors/?country={{country}}">{{country}}</a></div></th>
%end
</tr>
<tr>
%for country, sum in countries:
    <th class="n">{{n(sum)}}</th>
%end
</tr>
</thead>
<tbody>
%for analyser, sum in sorted(analysers_sum.items(), key=lambda k: -k[1]):
<tr>
    <th style="text-align: left">{{analyser}}</th>
    <th class="n">{{n(sum)}}</th>
%  for country, _ in countries:
    <td>{{n(analysers[analyser][country]) if country in analysers[analyser] else ''}}</td>
%  end
</tr>
%end
</tbody>
</table>
</div>
