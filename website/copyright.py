#! /usr/bin/env python
#-*- coding: utf-8 -*-

import sys, os, cgi
osmose_root = os.environ["OSMOSE_ROOT"]
sys.path.append(osmose_root)
from tools import utils

translate = utils.translator()
show = utils.show

utils.print_header(_("OsmOse - copyright informations"))

show(u"<b>%s</b>" % _("Data are coming from:"))
show(u"")

urls = []
urls.append(("OpenStreetMap", "http://www.openstreetmap.org/", "http://www.openstreetmap.org/copyright"))
urls.append(("OpenStreetBugs", "http://openstreetbugs.appspot.com/", None))
urls.append(("www.galichon.com", "http://www.galichon.com/", "http://www.galichon.com/codesgeo/avertissement.php"))

show(u"<ul>")
for u in urls:
  show(u"<li>")
  show(u"<a href='%s'>%s</a>" % (u[1], u[0]))
  if u[2]:
    show(u"(<a href='%s'>%s</a>)" % (u[2], _("copyright")))
  show(u"</li>")

show(u"</ul>")

utils.print_tail()

