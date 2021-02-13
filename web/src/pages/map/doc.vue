<template>
  <div id="docTpl" style="display: none">
    <template v-pre>{{={% %}=}}</template>
    <h5>ℹ {%title%}</h5>

    {%#detail%}
    <p>{%&amp;detail%}</p>
    {%/detail%}

    {%#fix%}
    <h6>✅ <translate>How to Fix</translate></h6>
    <p>{%&amp;fix%}</p>
    {%/fix%}

    {%#trap%}
    <h6>❌ <translate>Trap to avoid</translate></h6>
    <p>{%&amp;trap%}</p>
    {%/trap%}

    {%#example%}
    <h6><translate>Example</translate></h6>
    <p>{%&amp;example%}</p>
    {%/example%}

    {%#source_link%}
    <h6>🔗 <translate>Source Code</translate></h6>
    <p><a href="{%source_link%}" target="_blank">{%source_title%}</a></p>
    {%/source_link%}

    {%#resource_link%}
    <h6>🔗 <translate>Resource used</translate></h6>
    <p><a href="{%resource_link%}" target="_blank">{%resource_title%}</a></p>
    {%/resource_link%}

    <div id="doc_bottom">
      <p>
        <translate>Want to improve this control or this doc?</translate>
        <a
          href="https://wiki.openstreetmap.org/wiki/Osmose#Help_and_issues_description"
          target="_blank"
        >
          wiki.osm.org/Osmose#Help
        </a>
      </p>
    </div>
  </div>
</template>
