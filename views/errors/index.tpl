%from datetime import datetime
%favicon=None
%for res in items:
%    if item == str(res["item"]):
%        title += ' - ' + translate.select(res['menu'])
%        favicon = "../images/markers/marker-l-%s.png" % res["item"]
%    end
%end
%rss="http://"+website+"/errors.rss?%s" % query
%rebase('layout.tpl', title=title, favicon=favicon, rss=rss)
<nav class="navbar navbar-expand-lg navbar-dark" style="background-color: #212529;">
  <div class="collapse navbar-collapse">
    <div class="navbar-nav">
      <a class="nav-item nav-link active" href=".?{{query}}">{{_("Informations")}}</a>
      <a class="nav-item nav-link active" href="done?{{query}}">{{_("Fixed")}}</a>
      <a class="nav-item nav-link active" href="false-positive?{{query}}">{{_("False positives")}}</a>
      <a class="nav-item nav-link active" href="graph.png?{{query}}">{{_("Graph")}}</a>
      <a class="nav-item nav-link active" href="../map/#{{query}}">{{_("Map")}}</a>
    </div>
  </div>
</nav>
</br>

<div class="form-inline col-md-12">
<form method='get' action=''>
<div class="col-md-4" style="display:inline">
<select class="form-control form-control-sm" name='country'>
    <option value=''></option>
%for res in countries:
    <option\\
%    if country == res['country']:
 selected='selected'\\
%    end
 value='{{res['country']}}'>{{res['country']}}</option>
%end
</select>

<div class="col-md-4" style="display:inline">
<select class="form-control form-control-sm" name='item'>
    <option value='xxxx'></option>
%for res in items:
    <option\\
%    if str(item) == str(res['item']):
 selected='selected'\\
%    end
 value='{{res['item']}}'>{{res['item']}} - {{translate.select(res['menu'])}}</option>
%end
</select>
</div>

<div class="col-md-2" style="display:inline">
%# TRANSLATORS: 'Set' is used to choose a specific country/item on /errors
<input type='submit' class='btn btn-outline-secondary btn-sm' value='{{_("Set")}}'>
</div>
</div>

</form>
</div>

<table class="table table-striped table-bordered table-hover table-sm sortable" id ="table_source">
<thead class="thead-dark">
<tr>
    <th scope="col">#</th>
    <th scope="col">{{_("source")}}</th>
    <th scope="col">{{_("age")}}</th>
    <th scope="col" class="sorttable_sorted">{{_("item")}}<span id="sorttable_sortfwdindtable_source">&nbsp;▾</span></th>
%# TRANSLATORS: this should be replaced by a abbreviation for class
    <th scope="col" title="class">{{_("class (abbreviation)")}}</th>
    <th scope="col">{{_("title")}}</th>
    <th scope="col">{{_("count")}}</th>
</tr>
</thead>
<tbody>
%for res in errors_groups:
<tr>
    <td><a href="?source={{res["source"]}}">{{res["source"]}}</a></td>
    <td>{{res["analyser"]}}-<a href="?country={{res["country"]}}">{{res["country"]}}</a></td>
    <td>{{round((datetime.now(res["timestamp"].tzinfo) - res["timestamp"]).total_seconds()/60/60/24, 1)}}</td>
    <td>
        <img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}">
        <a href="?item={{res["item"]}}">{{res["item"]}}</a>
%        if res["menu"]:
            {{translate.select(res["menu"])}}
%        end
    </td>
    <td><a href="?item={{res["item"]}}&amp;class={{res["class"]}}">{{res["class"]}}</a></td>
    <td>{{translate.select(res["title"])}}</td>
%    count = res["count"]
%    if count == -1:
%        count = "N/A"
%    end
    <td><a href="?source={{res["source"]}}&amp;item={{res["item"]}}&amp;class={{res["class"]}}">{{count}}</a></td>
</tr>
%end
</tbody>
%if total > 0:
<tfoot class="thead-dark">
<tr>
    <th colspan="6">{{_("Total")}}</th>
    <th style="text-align: left">{{total}}</th>
</tr>
</tfoot>
%end
</table>
<br>
%if errors:
%    str_more = _("Show more issues")
%    include("views/errors/list.tpl", errors=errors, gen=gen, opt_date=opt_date, translate=translate, main_website=main_website, remote_url_read=remote_url_read, page_args="")
%
%    import urlparse, urllib
%    query_dict = urlparse.parse_qs(query)
%    limit = int((query_dict.has_key("limit") and query_dict["limit"][0])) or 20
%    if limit < total:
%        limit *= 5
%    end
%    query_dict["limit"] = limit
<br>
<a href="?{{urllib.urlencode(query_dict, True)}}">{{str_more}}</a>
%else:
<a href="?{{query}}&amp;limit=100">{{_("Show some issues")}}</a>
%end
