%favicon=None
%for res in items:
%    if item == res['item']:
%        title += ' - ' + translate.select(res['menu'])
%        favicon = "../images/markers/marker-l-%s.png" % res["item"]
%    end
%end
%rebase layout title=title, favicon=favicon
<a href=".?{{query}}">{{_("Informations")}}</a>
<a href="done?{{query}}">{{_("Fixed")}}</a>
<a href="false-positive?{{query}}">{{_("False positives")}}</a>
<a href="graph.png?{{query}}">{{_("Graph")}}</a>
<a href="../map/?{{query}}">{{_("Map")}}</a>
<br><br>

<form method='get' action=''>

<select name='country'>
    <option value=''></option>
%for res in countries:
    <option\\
%    if country == res['country']:
 selected='selected'\\
%    end
 value='{{res['country']}}'>{{res['country']}}</option>
%end
</select>

<select name='item'>
    <option value='xxxx'></option>
%for res in items:
    <option\\
%    if str(item) == str(res['item']):
 selected='selected'\\
%    end
 value='{{res['item']}}'>{{res['item']}} - {{translate.select(res['menu'])}}</option>
%end
</select>

%# TRANSLATORS: 'Set' is used to choose a specific country/item on /errors
<input type='submit' value='{{_("Set")}}'>

</form>

<table class="sortable" id ="table_source">
<thead>
<tr>
    <th>#</th>
    <th>{{_("source")}}</th>
%# TRANSLATORS: this should be replaced by a abbreviation for class
    <th title="class">{{_("class (abbreviation)")}}</th>
    <th></th>
    <th class="sorttable_sorted">#<span id="sorttable_sortfwdindtable_source">&nbsp;▾</span></th>
    <th>{{_("item")}}</th>
    <th>{{_("title")}}</th>
    <th>{{_("count")}}</th>
</tr>
</thead>
<tbody>
%for res in errors_groups:
<tr>
    <td><a href="?source={{res["source"]}}">{{res["source"]}}</a></td>
%    cmt_split = res["comment"].split("-")
%    analyse = "-".join(cmt_split[0:-1])
%    country = cmt_split[-1]
    <td>{{analyse}}-<a href="?country={{country}}">{{country}}</a></td>
    <td><a href="?item={{res["item"]}}&amp;class={{res["class"]}}">{{res["class"]}}</a></td>
    <td title="{{res["item"]}}"><img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}"></td>
    <td><a href="?item={{res["item"]}}">{{res["item"]}}</a></td>
%    if res["menu"]:
    <td>{{translate.select(res["menu"])}}</td>
%    else:
    <td></td>
%    end
    <td>{{translate.select(res["title"])}}</td>
%    count = res["count"]
%    if count == -1:
%        count = "N/A"
%    end:
    <td><a href="?source={{res["source"]}}&amp;item={{res["item"]}}&amp;class={{res["class"]}}">{{count}}</a></td>
</tr>
%end
</tbody>
%if total > 0:
<tfoot>
<tr>
    <th colspan="7">{{_("Total")}}</th>
    <th style="text-align: left">{{total}}</th>
</tr>
</tfoot>
%end
</table>
<br>
%if errors:
%    include views/errors/list.tpl errors=errors, gen=gen, opt_date=opt_date, translate=translate
%
%    import urlparse, urllib
%    query_dict = urlparse.parse_qs(query)
%    limit = int((query_dict.has_key("limit") and query_dict["limit"][0])) or 20
%    if limit < total:
%        limit *= 5
%    end
%    query_dict["limit"] = limit
<br>
<a href="?{{urllib.urlencode(query_dict, True)}}">{{translate.select("Show more errors")}}</a>
%else:
<a href="?{{query}}&amp;limit=100">{{_("Show some errors")}}</a>
%end
