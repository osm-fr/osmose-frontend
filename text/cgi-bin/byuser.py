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

import sys, os, cgi
osmose_root = os.environ["OSMOSE_ROOT"]
sys.path.append(osmose_root)
from tools import utils

PgConn    = utils.get_dbconn()
PgCursor  = PgConn.cursor()
form      = cgi.FieldStorage()
username  = utils.pg_escape(form.getvalue("username", ""))
#username="yoann"
lang_def  = utils.allowed_languages[0]
lang_cur  = utils.get_language()
tpl       = open(os.path.join(utils.root_folder, "config/text.tpl")).read()

if username=="":
    print "Content-Type: text/html; charset=utf-8"
    print
    print open("../index.html").read()
    sys.exit(0)

PgCursor.execute("SELECT * FROM dynpoi_marker WHERE (source,class,subclass,elems) IN (SELECT source,class,subclass,elems FROM dynpoi_user WHERE username='%s') LIMIT 500;"%(username))
#PgCursor.execute("SELECT dynpoi_marker.* FROM dynpoi_user NATURAL INNER JOIN dynpoi_marker WHERE dynpoi_user.username='%s' ORDER BY dynpoi_marker.class,dynpoi_marker.subclass,dynpoi_marker.elems;"%(username))
data = ""
for res in PgCursor.fetchall():
    data += '<div class="div_text"><font size="-1">\n'
    if res["html_"+lang_cur]:
        data += res["html_"+lang_cur]+"\n"
    else:
        data += res["html_"+lang_def]+"\n"
    data += '</font></div>\n'

print "Content-Type: text/html; charset=utf-8"
print
#print username
print tpl.replace("#data#", data)
