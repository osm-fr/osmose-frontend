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
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

PgConn    = utils.get_dbconn()
PgCursor  = PgConn.cursor()
form      = cgi.FieldStorage()

###########################################################################

print "Content-Type: text/html; charset=utf-8"
print

err = form.getvalue("e", "").split("-")
source_id = int(err[0])
class_id  = int(err[1])
sub_class = int(err[2])
elems     = utils.pg_escape(err[3])

status    = form.getvalue("s", None)
if status not in ["done","false"]:
    sys.exit(0)

## OpenStreetBugs
if source_id==62:
    import commands
    s, o = commands.getstatusoutput("wget -o /dev/null -O - 'http://openstreetbugs.schokokeks.org/api/0.1/closePOIexec?id=%d'"%sub_class)
    if o.strip() <> "ok":
        print "ERROR UPDATING OpenStreetBugs"
        sys.exit(1)
## Other sources
else:
    PgCursor.execute("DELETE FROM dynpoi_status WHERE source=%d AND class=%d AND subclass=%d AND elems='%s';"%(source_id,class_id,sub_class,elems))
    PgCursor.execute("INSERT INTO dynpoi_status (source,class,subclass,elems,date,status) VALUES (%d,%d,%d,'%s',NOW(),'%s');"%(source_id,class_id,sub_class,elems,status))
    
#PgCursor.execute("DELETE FROM dynpoi_marker WHERE (source,class,subclass,elems) IN (SELECT source,class,subclass,elems FROM dynpoi_status);")
PgCursor.execute("DELETE FROM dynpoi_marker WHERE source=%d AND class=%d AND subclass=%d AND elems='%s';"%(source_id, class_id, sub_class, elems))
PgConn.commit()

print "OK"
