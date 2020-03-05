{{!mustache_delimiter}}
<h5>ℹ {%title%}</h5>

{%#detail%}
<p>{%&detail%}</p>
{%/detail%}

{%#fix%}
<h6>✅ {{_('How to Fix')}}</h6>
<p>{%&fix%}</p>
{%/fix%}

{%#trap%}
<h6>❌ {{_('Trap to avoid')}}</h6>
<p>{%&trap%}</p>
{%/trap%}

{%#example%}
<h6>{{_('Example')}}</h6>
<p>{%&example%}</p>
{%/example%}

{%#source_link%}
<h6>🔗 {{_('Source Code')}}</h6>
<p><a href="{%source_link%}" target="_blank">{%source_title%}<a/></p>
{%/source_link%}

{%#resource_link%}
<h6>🔗 {{_('Resource used')}}</h6>
<p><a href="{%resource_link%}" target="_blank">{%resource_title%}<a/></p>
{%/resource_link%}

<div id="doc_bottom">
<p>{{_('Want to improve this control or this doc?')}} <a href="https://wiki.openstreetmap.org/wiki/Osmose#Help_and_issues_description" target="_blank">wiki.osm.org/Osmose#Help</a></p>
</div>
