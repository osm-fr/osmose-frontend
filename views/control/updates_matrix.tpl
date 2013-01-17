%rebase layout title=_("Last updates")
%def col(t, v):
%            if v > 4:
    <{{t}} class="delay-error">\\
%            elif v > 2:
    <{{t}} class="delay-warning">\\
%            else:
    <{{t}}>\\
%            end

%end
<div style="font-size:50%">
<table>
<tr>
    <th colspan="3" rowspan="3"/>
%for k in keys:
    <th class="country"><div class="rotate-90"><a href="../errors/?country={{k}}">{{k}}</a></div></th>
%end
</tr>
<tr>
%for k in keys:
%    col('th', stats_country[k][0])
{{"%0.1f"%stats_country[k][0]}}</th>
%end
</tr>
<tr>
%for k in keys:
%    col('th', stats_country[k][0])
{{"%0.1f"%stats_country[k][1]}}</th>
%end
</tr>
%for r in sorted(matrix.keys()):
<tr>
    <th style="text-align: left">{{r}}</th>
%    col('th', stats_analyser[r][0])
{{"%0.1f"%stats_analyser[r][0]}}</th>
%    col('th', stats_analyser[r][1])
{{"%0.1f"%stats_analyser[r][1]}}</th>
%    for k in keys:
%        if matrix[r].has_key(k):
%            v = matrix[r][k][1]
%            col('td', v)
<a href="update/{{matrix[r][k][2]}}">{{"%0.1f"%v}}</a></td>
%        else:
    <td/>
%        end
%    end
</tr>
%end
</table>
</div>
