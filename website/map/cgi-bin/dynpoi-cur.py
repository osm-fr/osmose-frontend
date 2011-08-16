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

###########################################################################
## database connection

import sys, os, cgi, Cookie, datetime
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

PgConn   = utils.get_dbconn()
PgCursor = PgConn.cursor()

###########################################################################
## form fields

form = cgi.FieldStorage()

lat    = int(float(form.getvalue("lat", "0"))*1000000)
lon    = int(float(form.getvalue("lon", "0"))*1000000)
err_id = form.getvalue("item", "").split(",")
err_id = ",".join([str(int(x)) for x in err_id if x])
source = form.getvalue("source", "")
user   = form.getvalue("user", "")
zoom   = int(form.getvalue("zoom", "0"))
bbox   = form.getvalue("bbox", None).split(",")
minlon = int(1000000*float(bbox[0]))
minlat = int(1000000*float(bbox[1]))
maxlon = int(1000000*float(bbox[2]))
maxlat = int(1000000*float(bbox[3]))
bbox   = "(dynpoi_marker.lat BETWEEN %d AND %d) AND (dynpoi_marker.lon BETWEEN %d and %d)"%(minlat, maxlat, minlon, maxlon)

###########################################################################
## page headers

print "Content-Type: text/plain; charset=utf-8"

cki = Cookie.SimpleCookie()
if os.environ.has_key('HTTP_COOKIE'):
    cki.load(os.environ['HTTP_COOKIE'])
cki["lastLat"] = form.getvalue("lat", "0")
cki["lastLat"]['expires'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%a, %d %b %Y %H:00:00 GMT")
cki["lastLat"]['path']    = '/'
cki["lastLon"] = form.getvalue("lon", "0")
cki["lastLon"]['expires'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%a, %d %b %Y %H:00:00 GMT")
cki["lastLon"]['path']    = '/'
cki["lastZoom"] = form.getvalue("zoom", "0")
cki["lastZoom"]['expires'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%a, %d %b %Y %H:00:00 GMT")
cki["lastZoom"]['path']    = '/'
cki["lastItem"] = form.getvalue("item", "")
cki["lastItem"]['expires'] = (datetime.datetime.now() + datetime.timedelta(days=365)).strftime("%a, %d %b %Y %H:00:00 GMT")
cki["lastItem"]['path']    = '/'
if cki:
    print cki
            
###########################################################################
## data

print
print "\t".join(["lat", "lon", "marker_id", "icon", "iconSize", "iconOffset", "html"])


if (not user) and (not source) and (zoom < 8):
    sys.exit(0)

#diff = 2.0*1000*1000

lang_def = utils.allowed_languages[0]
lang_cur = utils.get_language()
sqlbase  = """SELECT dynpoi_marker.item, dynpoi_marker.source, dynpoi_marker.class, dynpoi_marker.elems, dynpoi_marker.subclass, marker_id, lat, lon, html_%s as html_cur, html_%s as html_def
FROM dynpoi_marker %s
ORDER BY ABS(lat-%d)+ABS(lon-%d) ASC
LIMIT 100;"""

if source:
    sources = source.split(",")
    source2 = []
    for source in sources:
        source = source.split("-")
        if len(source)==1:
            source2.append("(dynpoi_marker.source=%d)"%int(source[0]))
        else:
            source2.append("(dynpoi_marker.source=%d AND dynpoi_marker.class=%d)"%(int(source[0]), int(source[1])))
    sources2 = " OR ".join(source2)
    #where = "WHERE (%s) AND (dynpoi_marker.lat <> 0 OR dynpoi_marker.lon <> 0) AND (%s)"%(sources2, bbox)
    where = "WHERE (%s) AND (%s)"%(sources2, bbox)
    sql =  sqlbase%(lang_cur, lang_def, where, lat, lon)
elif user:
    sys.exit(0)
elif err_id:
    #if user:
    #    where = "INNER JOIN dynpoi_user ON (dynpoi_marker.source, dynpoi_marker.class, dynpoi_marker.subclass, dynpoi_marker.elems) = (dynpoi_user.source, dynpoi_user.class, dynpoi_user.subclass, dynpoi_user.elems) WHERE dynpoi_user.username='%s'"%(utils.pg_escape(user))
    #where = "WHERE (item IN (%s)) AND (dynpoi_marker.lat <> 0 OR dynpoi_marker.lon <> 0) AND (%s)"%(err_id,bbox)
    where = "WHERE (item IN (%s)) AND (%s)"%(err_id,bbox)
    sql =  sqlbase%(lang_cur, lang_def, where, lat, lon)
else:
    sys.exit(0)

###########################################################################
## sql querry


sql = sql.replace("--","+")
#print sql
PgCursor.execute(sql)

try:
    open("/tmp/osmose-last.sql","w").write(sql+"\n")
except:
    pass

###########################################################################
## printing results

for res in PgCursor.fetchall():
    
    lat      = str(float(res["lat"])/1000000)
    lon      = str(float(res["lon"])/1000000)
    
    error_id = "%d-%d-%d-%s-%d" % (res["source"], res["class"], res["subclass"], res["elems"], res["marker_id"])
    
    if res["html_cur"]:
        html = res["html_cur"]
    elif res["html_def"]:
        html = res["html_def"]
    else:
        continue
    html = "<div style=\"float:right;margin-right:20;color:#EEEEEE;font-weight:bold;background-color:#AAAAAA;\" onclick=\"closeBubble('%s');\"><b>&nbsp;X&nbsp;</b></div>"%error_id + html
    
    marker   = "../markers/marker-b-%d.png" % (res["item"])
    
    print "\t".join([lat, lon, error_id, marker, "17,33", "-8,-33", "<font size=\"-1\">%s</font>"%html])
