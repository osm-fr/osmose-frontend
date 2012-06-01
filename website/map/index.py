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
if "lastItem" in cki:
    active_items = cki.get("lastItem").value.split(",")
    
# valeurs du formulaire
if form.getvalue("lat", None):
    dico["lat"]  = form.getvalue("lat", None)
if form.getvalue("lon", None):
    dico["lon"]  = form.getvalue("lon", None)
if form.getvalue("zoom", None):
    dico["zoom"] = form.getvalue("zoom", None)
if form.getvalue("item", None):
    active_items = form.getvalue("item", None).split(",")

try:
    active_items = [int(x) for x in active_items if x]
except:
    active_items = all_items
    
dico["form"]      = u""
dico["title"]     = _("OsmOse - map")
dico["need_zoom"] = _("no bubbles at this zoom factor")

###########################################################################
## formulaire

for categ in categories:
    
    dico["form"] += "<div class=\"test_group\" id=\"categ%d\">\n"%(categ["categ"])
    
    dico["form"] += "<h1><a href=\"javascript:toggleCategDisplay('categ%d')\">%s</a> "%(categ["categ"], categ["menu"])
    dico["form"] += "<span id=\"categ%d_count\">%d/%d</span> "%(categ["categ"], len([x for x in categ["item"] if x["item"] in active_items]), len(categ["item"]))
    dico["form"] += "<a href=\"javascript:showHideCateg('categ%d', true)\">Tout</a> "%(categ["categ"])
    dico["form"] += "<a href=\"javascript:showHideCateg('categ%d', false)\">Rien</a></h1>"%(categ["categ"])
    dico["form"] += "\n"
    
    for err in categ["item"]:
        dico["form"] += "<img vspace='0' src=\"markers/marker-l-%d.png\" alt=\"\">\n"%(err["item"])
        dico["form"] += "<input type='checkbox' id='item%d' name='item%d' onclick='checkbox_click(this)'%s>\n"%(err["item"], err["item"], {True:" checked=\"checked\"", False:""}[err["item"] in active_items])
        dico["form"] += u"<span class=\"check\"><a href=\"../utils/info.py?item=%d\">%s</a></span><br>\n"%(err["item"],err["menu"])
            
    dico["form"] += "</div>\n"
        
    dico["form"] += "\n"
    
###########################################################################
## template et envoi

if __name__ == "__main__":
    print "Content-Type: text/html; charset=utf-8"
    print
    #print active_items
    page = open(os.path.join(root_folder, "config/map.tpl")).read().decode("utf8")
    for x in dico:
        page = page.replace("#%s#"%x, dico[x].strip())
    print page.encode("utf8")
