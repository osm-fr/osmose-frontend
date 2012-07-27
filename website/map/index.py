#! /usr/bin/env python
#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

import sys, os, cgi, Cookie
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

PgConn     = utils.get_dbconn()
PgCursor   = PgConn.cursor()
translate  = utils.translator()
form       = cgi.FieldStorage()

###########################################################################
## structure du menu

categories = utils.get_categories()
show = utils.show

###########################################################################
## liste de toutes les erreurs
    
all_items = []
PgCursor.execute("SELECT item FROM dynpoi_item GROUP BY item;")
for res in PgCursor.fetchall():
    all_items.append(int(res[0]))

###########################################################################
## dictionnaire des infos pour le template

dico = {}

# valeurs par défaut
dico["lat"]    = "46.97"
dico["lon"]    = "2.75"
dico["zoom"]   = "6"
level          = "1"
dico["source"] = form.getvalue("source", "")
dico["user"]   = form.getvalue("user", "")

active_items   = all_items

# valeurs du cookie
cki = Cookie.SimpleCookie()
if os.environ.has_key('HTTP_COOKIE'):
    cki.load(os.environ['HTTP_COOKIE'])
if "lastLat" in cki:
    dico["lat"] = cki.get("lastLat").value
if "lastLon" in cki:
    dico["lon"] = cki.get("lastLon").value
if "lastZoom" in cki:
    dico["zoom"] = cki.get("lastZoom").value
if "lastLevel" in cki:
    level = cki.get("lastLevel").value
if "lastItem" in cki:
    active_items = cki.get("lastItem").value.split(",")
    
# valeurs du formulaire
if form.getvalue("lat", None):
    dico["lat"]  = form.getvalue("lat", None)
if form.getvalue("lon", None):
    dico["lon"]  = form.getvalue("lon", None)
if form.getvalue("zoom", None):
    dico["zoom"] = form.getvalue("zoom", None)
if form.getvalue("level", None):
    level = form.getvalue("level", None)
if form.getvalue("item", None):
    active_items = form.getvalue("item", None).split(",")

try:
    active_items = [int(x) for x in active_items if x]
except:
    active_items = all_items


for l in ("_all", "1", "2", "3", "1,2", "1,2,3"):
    dico["level%s" % l] = ""

if level == "":
    dico["level1"] = " selected"
elif level in ("1", "2", "3", "1,2", "1,2,3"):
    dico["level%s" % level] = " selected"

dico["form"]      = u""
dico["title"]     = _("OsmOse - map")
dico["need_zoom"] = _("no bubbles at this zoom factor")
dico["check"]         = _("Select:")
dico["check_all"]     = _("all")
dico["check_nothing"] = _("nothing")
dico["check_invert"]  = _("invert")
dico["level_all_str"] = _("all levels")

dico["item_levels"] = u""

###########################################################################
## formulaire

for categ in categories:
    
    dico["form"] += "<div class=\"test_group\" id=\"categ%d\">\n"%(categ["categ"])
    
    dico["form"] += "<h1><a href=\"javascript:toggleCategDisplay('categ%d')\">%s</a> "%(categ["categ"], categ["menu"])
    dico["form"] += "<span id=\"categ%d_count\">%d/%d</span> "%(categ["categ"], len([x for x in categ["item"] if x["item"] in active_items]), len(categ["item"]))
    dico["form"] += "<a href=\"javascript:showHideCateg('categ%d', true)\">%s</a> "%(categ["categ"], _("all"))
    dico["form"] += "<a href=\"javascript:showHideCateg('categ%d', false)\">%s</a></h1>"%(categ["categ"], _("nothing"))
    dico["form"] += "\n"
    dico["form"] += "<ul>"
    
    for err in categ["item"]:
        dico["form"] += "<li style='background-image: url(markers/marker-l-%d.png)' id='item_desc%d'>" % (err["item"], err["item"])
        dico["form"] += "<input type='checkbox' id='item%d' name='item%d' onclick='checkbox_click(this)'%s>\n"%(err["item"], err["item"], {True:" checked=\"checked\"", False:""}[err["item"] in active_items])
        s_l = ["."] * 3
        for l in err["levels"]:
            s_l[l-1] = str(l)
        dico["form"] += u"<a href=\"../utils/info.py?item=%d\">%s</a><div>%s</div>\n"%(err["item"],err["menu"], "".join(s_l))
        dico["form"] += u"</li>"
            
    dico["form"] += "</ul>"
    dico["form"] += "</div>\n"
        
    dico["form"] += "\n"

levels = {"1": set(), "2": set(), "3": set()}

for categ in categories:
    for err in categ["item"]:
        for l in err["levels"]:
            levels[str(l)].add(err["item"])

levels["1,2"] = levels["1"] | levels["2"]
levels["1,2,3"] = levels["1,2"] | levels["3"]

for (l, i) in levels.iteritems():
    dico["item_levels"] += "item_levels[\"%s\"] = %s;\n" % (l, list(i))



###########################################################################
## template et envoi

utils.print_template("map.tpl", dico)

urls = []
# TRANSLATORS: link to help in appropriate language
urls.append((_("Help"), _("http://wiki.openstreetmap.org/wiki/Osmose")))
urls.append((_("by user"), "/text"))
urls.append((_("relation analyser"), "http://analyser.openstreetmap.fr/"))
# TRANSLATORS: this link can be changed to something specific to the language
urls.append((_("clc"), _("http://clc.openstreetmap.fr/")))
# TRANSLATORS: this link can be changed to something specific to the language
urls.append((_("geodesic"), _("http://geodesie.openstreetmap.fr/")))
# TRANSLATORS: this link can be changed to something specific to the language
urls.append((_("openstreetmap.fr"), _("http://www.openstreetmap.fr/")))
urls.append((_("copyright"), "/copyright.py"))
# TRANSLATORS: link to source code
urls.append((_("sources"), "https://gitorious.org/osmose"))
urls.append((_("statistics"), "/utils/last-update.py"))

show(u"<div id='bottom_links'>")

show(u"<div style='float: left'>")
show(u"<form method='get' style='display:inline'>")
show(u"<select name='language'>")
show(u"<option value='' onclick='set_lang(\"\");'></option>")
for l in utils.allowed_languages:
  if translate.languages[0] == l:
    s = " selected='selected'"
  else:
    s = ""
  show(u"<option%s value='%s' onclick='set_lang(\"%s\");'>%s</option>" % (s, l, l, l))
show(u"</select>")
show(u"</form>")
show(u"</div>")

show(u"  <div id='links'>")
s = []
for u in urls:
  s.append(u"<a href='%s'>%s</a>" % (u[1], u[0]))
show(u" - ".join(s))
show(u"  </div>")
show(u"</div>")

utils.print_tail()
