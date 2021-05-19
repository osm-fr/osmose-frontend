<p>{{ res["item"] }}({{ res["level"] }})/{{ res["class"] }} {{ res["uuid"] }}</p>
%if res['elems']:
    %for e in res['elems']:
        <p>
            <a href="{{ main_website }}{{ e["type_long"] }}/{{ e["id"] }}">{{ _(e["type_long"]) }} {{ e["id"] }}</a>&nbsp
            <a href="{{ map_url }}">Osmose</a>&nbsp
            <a href="{{ e["object_josm_url"] }}">JOSM</a>&nbsp
            <a href="{{ e["object_id_url"] }}">iD</a>
        </p>
        %if "tags" in e:
            <p>
                {{ _("Tags") }}:
                <ul>
                %for k, v in e['tags'].items():
                    <li>{{ k }}={{ v }}</li>
                %end
                </ul>
            </p>
        %end
    %end
%else:
    <a href="{{ fallback_url }}"></a>
%end
<a href="{{ website }}/api/0.3/issue/{{ res["uuid"] }}/done">{{ _("Mark issue as fixed") }}</a>
<a href="{{ website }}/api/0.3/issue/{{ res["uuid"] }}/false">{{ _("Mark issue as false positive") }}</a>
<p>{{ _("Issue reported on:") }} {{ res["timestamp"].strftime("%Y-%m-%d") }}</p>
