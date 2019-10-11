%rebase('layout.tpl', title=(_("How to help translation")))
<h1>{{_("How to help translation")}}</h1>
<p>{{_("Osmose tool is mainly developped by french people, and we aim to add more languages.")}}
<p>{{_("To make Osmose a real multi-lingual tool, we need your help to improve current translations, and add new translations")}}</p>


<h2>{{_("Pages to translate")}}</h2>
<h3>{{_("Osmose pages")}}</h3>
<ul>
<li>{{!_("Translation is done on <a href='%s'>Transifex</a>.") % "http://www.transifex.com/projects/p/osmose/"}}</a></li>
</ul>
<div style="transifex-chart">
  <a target="_blank" style="text-decoration:none; color:black; font-size:66%" href="https://www.transifex.com/projects/p/osmose" title="See more information on Transifex.com">{{_("Translation progress: osmose")}}</a><br/>
  <a target="_blank" href="https://www.transifex.com/projects/p/osmose/"><img border="0" src="https://www.transifex.com/projects/p/osmose/chart/image_png"/></a><br/>
  <a target="_blank" href="https://www.transifex.com/projects/p/osmose/"><img border="0" src="https://ds0k0en9abmn1.cloudfront.net/static/charts/images/tx-logo-micro.646b0065fce6.png"/></a>
</div>

<h3>{{_("Wiki pages")}}</h3>
<ul>
<li><a href="{{_("http://wiki.openstreetmap.org/wiki/Osmose")}}">{{_("Osmose QA main page")}}</a></li>
<li><a href="{{_("http://wiki.openstreetmap.org/wiki/Osmose/errors")}}">{{_("Documentation on reported issues")}}</a></li>
</ul>

<h2>{{_("For new language or countries")}}</h2>
<ul>
<li>{{!_("You can create a new language directly on <a href='%s'>Transifex.</a>") % "http://www.transifex.com/projects/p/osmose/"}}</a></li>
<li>{{!_("For new countries, we can be contacted through a direct email to <a href='mailto:{email}'>{email}</a>.") .format (email="osmose-contact@openstreetmap.fr".replace('@', '&#x40;'))}}</li>
</li>
</ul>


<h2>{{_("Bug tracking system")}}</h2>
<ul>
<li>{{!_("<a href='https://github.com/osm-fr/osmose-frontend/issues'>osmose-frontend</a> can be used to report any issue with translations.")}}</a></li>
</ul>
