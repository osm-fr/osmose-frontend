%rebase('layout.tpl', title=_("Information on issue %d") % err_id, favicon="../images/markers/marker-l-%s.png" % marker['item'])
%def show_html_dict(dict):
            <table>
%            for (k, v) in sorted(dict.items()):
                <tr><td>{{k}}</td><td>{{v}}</td></tr>
%            end
            </table>
%end
%def show_html_list(list):
            <table>
%            for e in list:
                <tr><td>
%    if type(e) is dict:
%        show_html_dict(e)
%    elif type(e) is list:
%        if len(e) > 0:
%            show_html_list(e)
%        end
%    else:
{{e}}
%    end
</td></tr>
%            end
            </table>
%end
%def show_html_results(columns, res):
<table class="table table-striped table-bordered table-hover table-sm sortable" id ="table_marker">
<thead class="thead-dark">
<tr>
    <th scope="col">{{_("key")}}</th>
    <th scope="col">{{_("value")}}</th>
</tr>
</thead>
%    i = 0
%    for c in columns:
%        c = c.split(" ")[-1]
<tr>
    <td>{{c}}</td>
    <td>
%        if type(res[i]) is dict:
%            show_html_dict(res[i])
%        elif type(res[i]) is list:
%            if len(res[i]) > 0:
%                show_html_list(res[i])
%            end
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
<table class="table table-striped table-bordered table-hover table-sm sortable" id ="table_marker">
<thead class="thead-dark">
<tr>
    <th scope="col">{{_("key")}}</th>
    <th scope="col">{{_("value")}}</th>
</tr>
</thead>
<tr><td>source</td><td><a target="_blank" href="/errors/?item=xxxx&amp;source={{marker['source']}}">{{marker['source']}}<a></td></tr>
<tr><td>item</td><td><a target="_blank" href="/errors/?item={{marker['item']}}">{{marker['item']}}</a></td></tr>
<tr><td>class</td><td><a target="_blank" href="/errors/?item={{marker['item']}}&amp;class={{marker['class']}}">{{marker['class']}}</a></td></tr>
<tr><td>subclass</td><td><a target="_blank" href="/errors/?item={{marker['item']}}&amp;class={{marker['class']}}&subclass={{marker['subclass']}}">{{marker['subclass']}}</a></td></tr>
<tr><td>elems</td><td>{{marker['elems']}}</td></tr>
<tr><td>lat lon</td><td><a target="_blank" href="/map/?item={{marker['item']}}&amp;zoom=17&amp;lat={{marker['lat']}}&amp;lon={{marker['lon']}}">{{marker['lat']}}&nbsp;{{marker['lon']}}</a></td></tr>
<tr><td>title</td><td>
%show_html_dict(marker['title'])
</td></tr>
<tr><td>subtitle</td><td>
%show_html_dict(marker['subtitle'])
</td></tr>
<tr><td>timestamp</td><td>{{marker['timestamp']}}</td></tr>
</table>
</br>

<h2>{{_("Elements")}}</h2>
%for element in elements:
<table class="table table-striped table-bordered table-hover table-sm sortable" id ="table_marker">
<thead class="thead-dark">
<tr>
    <th scope="col">{{_("key")}}</th>
    <th scope="col">{{_("value")}}</th>
</tr>
</thead>
<tr><td>elem_index</td><td>{{element['elem_index']}}</td></tr>
<tr><td>type id</td><td><a target="_blank" href="{{main_website}}{{data_type[element['data_type']]}}/{{element['id']}}">{{element['data_type']}}&nbsp;{{element['id']}}</a></td></tr>
<tr><td>tags</td><td>
%     show_html_list(element['tags'])
</td></tr>
<tr><td>username</td><td><a target="_blank" href="{{main_website}}user/{{element['username']}}">{{element['username']}}</a></td></tr>
</table>
</br>
%end

<h2>{{_("Fixes")}}</h2>
%for i in fix:
%    show_html_results(columns_fix, i)
</br>
%end
