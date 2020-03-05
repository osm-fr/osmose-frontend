%rebase('layout.tpl', title=_("Contact"))
<h1>{{_("Bug tracker")}}</h1>
<p>{{! _("Bug should be reported on <a href='https://github.com/osm-fr/osmose-frontend/issues'>osmose-frontend</a> for issues around the website, or on <a href='https://github.com/osm-fr/osmose-backend/issues'>osmose-backend</a> for issues on the reported issues on OSM data, or for suggestion about analyses.")}}</p>

<h1>{{_("Providing patches")}}</h1>
<p>{{_("Patches can be provided via merge requests on Github. This is the preferred way of handling patches.")}}</p>
<ul>
  <li>Github:
  <ul>
    <li> <a href="https://github.com/osm-fr/osmose-backend">backend</a>
    <li> <a href="https://github.com/osm-fr/osmose-frontend">frontend</a>
  </ul>
</ul>

<h1>{{_("Development")}}</h1>
<p>{{! _("Development of Osmose is made as free software by <a href='../copyright'>volunteers</a>.")}}</p>
<p>{{! _(u"Adding new functionality of <em>Osmose Editor</em>, initial support of mobile device and improvement of documentation was funded by region of Aquitaine, France; part of the OpenAquiMap project leading by <em>Les Petits Débrouillards d'Aquitaine</em>.")}}</p>
<p>{{! _(u"The servers analysing data are provided by OpenStreetMap-France and some others by contributors around the world. The servers for north-america and other areas are funded by Mapbox.")}}</p>
<img src="images/logo-aquitaine.png" alt="Logo of region of Aquitaine" width="340" height="100"/>
<img src="images/logo-mapbox.png" alt="Logo of Mapbox" width="340" height="100"/>

<h1>{{_("Contacting maintainers")}}</h1>
<p>{{! _("We can be contacted through a direct email to <a href='mailto:{email}'>{email}</a>.").format(email="osmose-contact@openstreetmap.fr".replace('@', '&#x40;'))}}</p>
<p>{{! _("Keep in touch by watching at <a href='https://twitter.com/osmose_qa'>@osmose_qa</a> on twitter.")}}</p>
