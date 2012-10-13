%rebase layout title=_("Copyright informations")
<b>{{_("Data are coming from:")}}</b>

%urls = []
%urls.append(("OpenStreetMap", "http://www.openstreetmap.org/", "http://www.openstreetmap.org/copyright"))
%urls.append(("OpenStreetBugs", "http://openstreetbugs.appspot.com/", None))
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
