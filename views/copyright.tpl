%rebase('layout.tpl', title=_("Copyright informations"))
<h1>{{_("License")}}</h1>
<p>This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.</p>
<p>This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.</p>
<p>You should have received a copy of the GNU General Public License
along with this program.  If not, see http://www.gnu.org/licenses/.</p>

<h1>{{_("Authors")}}</h1>
<ul>
    <li>Etienne Chové 2009-2010</li>
    <li>Jocelyn Jaubert 2011-2013</li>
    <li>Frédéric Rodrigo 2011-2013</li>
</ul>
{{_("And contributors")}}
<ul>
    <li>Krysst aka Didier Marchand 2012</li>
    <li>Clément Cunin aka Black Myst 2012-2013</li>
    <li>Operon 2012-2013</li>
</ul>

<h1>{{_("Data are coming from")}}</h1>

%urls = []
%urls.append(("OpenStreetMap", "http://www.openstreetmap.org/", "http://www.openstreetmap.org/copyright"))
%urls.append(("www.galichon.com", "http://www.galichon.com/", "http://www.galichon.com/codesgeo/avertissement.php"))

<ul>
%for u in urls:
  <li>
    <a href='{{u[1]}}'>{{u[0]}}</a>
%  if u[2]:
    (<a href='{{u[2]}}'>{{_("copyright")}}</a>)
%  end
  </li>
%end
</ul>
