%from datetime import datetime
%favicon=None
%for res in items:
%    if item == str(res["item"]):
%        title += ' - ' + translate.select(res['menu'])
%        favicon = "../images/markers/marker-l-%s.png" % res["item"]
%    end
%end
%rss="http://"+website+"/"+lang+"/errors.rss?%s" % query
%rebase('layout.tpl', title=title, favicon=favicon, rss=rss)
<nav class="navbar navbar-expand-sm navbar-expand-md navbar-expand-lg navbar-dark" style="background-color: #212529;">
%if favicon:
  <span class="navbar-brand">
    <img src="{{favicon}}">
  </span>
%end
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

<div class="form-inline col-sm-12 col-md-12">
<form method='get' action='' id="errors-list">
<div class="form-row">
  <div class="form-group col-sm-3 col-md-3">
    <label for='item'>{{_("Country")}}</label>
    <select class="form-control form-control-sm" name='country'>
      <option value=''></option>
%for res in countries:
      <option\\
%    if country == res:
 selected='selected'\\
%    end
 value='{{res}}'>{{res}}</option>
%end
    </select>
  </div>

  <div class="form-group col-sm-3 col-md-3">
    <label for='item'>{{_("Item")}}</label>
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

  <div class="form-group col-sm-3 col-md-3">
    <label for='level'>{{_("Severity")}}</label>
    <select name='level' class='form-control form-control-sm'>
      <option class="level-1__" value="1"{{" selected='selected'" if level == '1' else ""}}>{{_("High")}}</option>
      <option class="level-12_" value="1,2"{{" selected='selected'" if level == '1,2' else ""}}>{{_("Normal or higher")}}</option>
      <option class="level-123" value="1,2,3"{{" selected='selected'" if level == '1,2,3' else ""}}>{{_("All")}}</option>
      <option disabled="disabled"></option>
      <option class="level-_2_" value="2"{{" selected='selected'" if level == '2' else ""}}>{{_("Normal only")}}</option>
      <option class="level-__3" value="3"{{" selected='selected'" if level == '3' else ""}}>{{_("Low only")}}</option>
    </select>
  </div>

  <div class="form-group col-sm-3 col-md-3">
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
    <td><a href="?source={{res["source_id"]}}">{{res["source_id"]}}</a></td>
    <td>{{res["analyser"]}}-<a href="?country={{res["country"]}}">{{res["country"]}}</a></td>
    <td>{{round((datetime.now(res["timestamp"].tzinfo) - res["timestamp"]).total_seconds()/60/60/24, 1)}}</td>
    <td>
        <img src="../images/markers/marker-l-{{res["item"]}}.png" alt="{{res["item"]}}">
        <a href="?item={{res["item"]}}&amp;country={{res["country"]}}">{{res["item"]}}</a>
%        if res["menu"]:
            {{translate.select(res["menu"])}}
%        end
    </td>
    <td><a href="?item={{res["item"]}}&amp;class={{res["class"]}}&amp;country={{res["country"]}}">{{res["class"]}}</a></td>
    <td>{{translate.select(res["title"])}}</td>
%    count = res["count"]
%    if count == -1:
%        count = "N/A"
%    end
    <td><a href="?source={{res["source_id"]}}&amp;item={{res["item"]}}&amp;class={{res["class"]}}">{{count}}</a></td>
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
%    include("web/views/errors/list.tpl", errors=errors, gen=gen, opt_date=opt_date, translate=translate, main_website=main_website, remote_url_read=remote_url_read, page_args="")
%
%    import urllib
%    query_dict = urllib.parse.parse_qs(query)
%    limit = int(("limit" in query_dict and query_dict["limit"][0])) or 100
%    if limit < total:
%        limit *= 5
%    end
%    query_dict["limit"] = limit
<br>
<a href="?{{urllib.parse.urlencode(query_dict, True)}}">{{str_more}}</a>
%else:
<a href="?{{query}}&amp;limit=100">{{_("Show some issues")}}</a>
%end
