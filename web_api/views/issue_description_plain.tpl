{{ res["item"] }}({{ res["level"] }})/{{ res["class"] }} {{ res["uuid"] }}
%if res['elems']:
    %for e in res['elems']:
{{ main_website }}{{ e["type_long"] }}/{{ e["id"] }} {{ e["object_josm_url"] }}
{{ _("Tags") }}:
        %for k, v in e.get('tags', {}).items():
    {{ k }}={{ v }}
        %end
    %end
%else:
{{ fallback_url }}
%end
{{ _("Issue reported on:") }} {{ res["timestamp"].strftime("%Y-%m-%d") }}
