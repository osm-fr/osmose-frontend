%rebase('layout.tpl', title=_("Last updates"))
%def col(t, v):
%            if v > 4.05:
    <{{t}} class="delay-error">\\
%            elif v > 2.05:
    <{{t}} class="delay-warning">\\
%            else:
    <{{t}}>\\
%            end

%end
<div style="font-size:50%">
<table>
<tr>
    <th colspan="4" rowspan="4"/>
%keys = sorted(keys, key=lambda k: -stats_country[k][2])
%for k in keys:
    <th class="country"><div class="rotate-90"><a href="../errors/?country={{k}}">{{k}}</a></div></th>
%end
</tr>
%for i in range(0,3):
<tr>
%    for k in keys:
%        col('th', stats_country[k][i])
{{"%0.1f"%stats_country[k][i]}}</th>
%    end
</tr>
%end
%for r in sorted(matrix.keys(), key=lambda k: -stats_analyser[k][2]):
<tr>
    <th style="text-align: left">{{r}}</th>
%    for i in range(0,3):
%        col('th', stats_analyser[r][i])
{{"%0.1f"%stats_analyser[r][i]}}</th>
%    end
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
