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

import sys, os, time, urllib, tempfile, commands
import utils
from xml.sax import make_parser, handler
tpl = open(os.path.join(utils.root_folder, "config/text.tpl")).read()

###########################################################################
## logger

class printlogger:
    def log(self, text):
        print text

###########################################################################
## updater

def update(source, url, logger = printlogger()):
    
    source_id = int(source["id"])
        
    ## open connections
    dbconn = utils.get_dbconn()
    dbcurs = dbconn.cursor()
    dbcurs.execute("DELETE FROM dynpoi_marker WHERE source = %d;"%source_id)
    dbcurs.execute("DELETE FROM dynpoi_class WHERE source = %d;"%source_id)
    dbcurs.execute("DELETE FROM dynpoi_user WHERE source = %d;"%source_id)
    
    ## xml parser
    parser = make_parser()
    parser.setContentHandler(update_parser(source_id, source, url, dbcurs))
        
    ## download the file if needed
    if url.startswith("http://"):
        fname =  tempfile.mktemp()
        urllib.urlretrieve(url, fname)
        #mysock = urllib.urlopen(source["url"])
        #open(fname,'w').write(mysock.read())
        istemp = True
    else:
        fname = url
        istemp = False
            
    ## open the file
    if url.endswith(".bz2"):
        import bz2
        f = bz2.BZ2File(fname)
    elif url.endswith(".gz"):
        import gzip
        f = gzip.open(fname)
    else:
        f = open(fname)
        
    ## parse the file
    parser.parse(f)

    ## update subtitle_en from new errors
    dbcurs.execute("""SELECT * FROM dynpoi_marker
                      WHERE (source,class,subclass,elems) IN (SELECT source,class,subclass,elems FROM dynpoi_status WHERE source = %s)""",
                   (source_id, ))
    for res in dbcurs.fetchall():
        dbcurs.execute("""UPDATE dynpoi_status SET subtitle_en = %s, lat = %s, lon = %s
                          WHERE source = %s AND class = %s AND subclass = %s AND elems = %s""",
                       (res["subtitle_en"], res["lat"], res["lon"],
                        res["source"], res["class"], res["subclass"], res["elems"]))

    ## remove false positive no longer present
    dbcurs.execute("""DELETE FROM dynpoi_status
                      WHERE (source,class,subclass,elems) NOT IN (SELECT source,class,subclass,elems FROM dynpoi_marker WHERE source = %s) AND
                            source = %s AND
                            date < now()-interval '7 day'""",
                   (source_id, source_id, ))

    dbcurs.execute("""DELETE FROM dynpoi_marker
                      WHERE (source,class,subclass,elems) IN (SELECT source,class,subclass,elems FROM dynpoi_status WHERE source = %s)""",
                   (source_id, ))
    
    ## commit and close
    dbconn.commit()
    dbconn.close()
    
    ## close and delete
    f.close()
    del f
    if istemp:
        os.remove(fname)

class update_parser(handler.ContentHandler):
    
    def __init__(self, source_id, source_data, source_url, dbcurs):
        self._source_id        = source_id
        self._source_data      = source_data
        self._source_url       = source_url
        self._dbcurs           = dbcurs
        self._class_texts      = {}
        self._class_item       = {}
        self._copy_marker_name = tempfile.mktemp()
        self._copy_marker      = open(self._copy_marker_name, 'w')
        self._copy_user_name   = tempfile.mktemp()
        self._copy_user        = open(self._copy_user_name, 'w')
        
    def startElement(self, name, attrs):
        if name == u"analyser":
            ts = attrs.get("timestamp", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            self._dbcurs.execute("INSERT INTO dynpoi_update VALUES(%d, '%s', '%s', '%s');"%(self._source_id, utils.pg_escape(ts), utils.pg_escape(self._source_url), utils.pg_escape(os.environ.get('REMOTE_ADDR', ''))))
        elif name == u"error":
            self._class_id        = int(attrs["class"])
            self._class_sub       = int(attrs.get("subclass", u"0"))%2147483647
            self._error_elements  = []
            self._error_locations = []
            self._error_texts     = {}
            self._users           = []
        elif name == u"location":
            self._error_locations.append(dict(attrs))
        elif name == u"text":
            self._error_texts[attrs["lang"]] = attrs["value"]
        elif name in [u"node", u"way", u"relation", u"infos"]:
            self._elem = dict(attrs)
            if "user" in self._elem:
                self._users.append(self._elem["user"])
            self._elem[u"type"] = name
            self._elem_tags = {}
        elif name == u"tag":
            #if (self._elem[u"type"]<>"relation") or (attrs["k"] in ["type"])
            if attrs["k"].startswith("name:"):
                return
            if attrs["k"].startswith("is_in:"):
                return            
            if attrs["k"].startswith("tiger:"):
                return
            if attrs["k"].startswith("TMC:"):
                return
            self._elem_tags[attrs["k"]] = attrs["v"]
        elif name == u"class":
            self._class_id    = int(attrs["id"])
            self._class_item[self._class_id] = int(attrs["item"])
            self._class_texts[self._class_id] = {}
        elif name == u"classtext":
            self._class_texts[self._class_id][attrs["lang"]] = attrs
            
    def endElement(self, name):
        if name == u"error":
            ## to remove when all in en
            if "en" not in self._error_texts:
                self._error_texts["en"] = self._error_texts and u"no translation" or u""
            
            ## build all_elem
            all_elem   = u""
            for e in self._error_elements:
                all_elem  += e[u"type"] + e[u"id"] + "_"
            all_elem  = all_elem.rstrip("_")            
                
            ## build sql fields
            keys = ['source', 'class', 'subclass', 'elems', 'marker_id', 'lat', 'lon', 'item ']
            vals = [str(self._source_id), str(self._class_id), str(self._class_sub), u"'%s'"%utils.pg_escape(all_elem), '#MID#', '#LAT2#', '#LON2#', str(self._class_item[self._class_id])]
            val2 = list(vals)

            ## build data variable
            data = []
            for e in self._error_elements:
                data += [u"##"+e[u"type"],e[u"id"]]
                for t in e[u"tag"].items():
                    data += [t[0], t[1]]
            keys.append(u"data")
            if data:
                vals.append(u"ARRAY[%s]"%u",".join([u"'%s'"%utils.pg_escape(x) for x in data]))
            else:
                vals.append(u"NULL")
            
            ## localised subtitles
            for lang in utils.allowed_languages:                    
                keys.append("subtitle_%s"%lang)
                if lang in self._error_texts:
                    subtitle = self._error_texts[lang]
                else:
                    subtitle = self._error_texts[utils.allowed_languages[0]]
                if len(subtitle)<1000:
                    vals.append(u"'%s'"%utils.pg_escape(subtitle))
                else:
                    vals.append(u"'%s'"%utils.pg_escape(subtitle[:1000]+"[...]"))
            
            ## sql template
            sql1 = (u"INSERT INTO dynpoi_marker (" + u','.join(keys) + u") VALUES (" + u','.join(vals) + u");").encode('utf8')
            
            ## add data at all location
            cpt = 0
            for location in self._error_locations:
                cpt += 1
                                
                lat = float(location["lat"])
                lon = float(location["lon"])
                
                sql = sql1.replace("#MID#",str(cpt))
                sql = sql.replace("#LEFT#",  str(lon-0.004))
                sql = sql.replace("#RIGHT#", str(lon+0.004))
                sql = sql.replace("#TOP#",   str(lat+0.003))
                sql = sql.replace("#BOTTOM#",str(lat-0.003))
                sql = sql.replace("#LAT#",str(lat))
                sql = sql.replace("#LON#",str(lon))
                sql = sql.replace("#LAT2#",str(int(1000000*lat)))
                sql = sql.replace("#LON2#",str(int(1000000*lon)))
                self._dbcurs.execute(sql)
                
            ## add for all users
            for user in self._users:
                val = [str(self._source_id), str(self._class_id), str(self._class_sub), "'%s'"%utils.pg_escape(all_elem), u"'%s'"%utils.pg_escape(user)]
                sql = u"INSERT INTO dynpoi_user (source,class,subclass,elems,username) VALUES (" + u','.join(val) + u");"
                sql = sql.encode('utf8')
                self._dbcurs.execute(sql)

        if name in [u"node", u"way", u"relation", u"infos"]:
            self._elem[u"tag"] = self._elem_tags
            self._error_elements.append(self._elem)
            
        if name == u"class":
            ## to remove when translated
            if "en" not in self._class_texts[self._class_id]:
                self._class_texts[self._class_id]["en"] = {"title":u"no translation"}
            ##
            keys = ["source", "class", "item"]
            vals = [utils.pg_escape(self._source_id), utils.pg_escape(self._class_id), utils.pg_escape(self._class_item[self._class_id])]
            for lang in utils.allowed_languages:
                if lang in self._class_texts[self._class_id]:
                    title = self._class_texts[self._class_id][lang].get("title", u"no title")
                else:
                    title = self._class_texts[self._class_id][utils.allowed_languages[0]].get("title", u"no title")
                keys.append("title_%s"%lang)
                vals.append(u"'%s'"%utils.pg_escape(title))
            sql = u"INSERT INTO dynpoi_class (" + u','.join(keys) + u") VALUES (" + u','.join(vals) + u");"
            sql = sql.encode('utf8')
            self._dbcurs.execute(sql)

        #if name == u"analyser":
        #    
        #    self._copy_marker.close()
        #    #s, o = commands.getstatusoutput("psql -c 'COPY dynpoi_marker FROM STDIN;' -d %s %s < %s"%(utils.pg_base, utils.pg_user, self._copy_marker_name))
        #    #if s:
        #    #    print o
        #    #self._dbcurs.execute("COPY dynpoi_marker FROM '%s';"%self._copy_marker_name)
        #    
        #    #self._copy_user.close()
        #    #self._dbcurs.execute("COPY dynpoi_user FROM '%s';"%self._copy_user_name)
            
###########################################################################
                        
def show(source):
    print "source #%s"%source["id"]
    for k in source:
        if k == "id":
            continue
        if type(source[k])== list:
            for e in source[k]:
                print "   %-10s = %s"%(k, e)
        else:
            print "   %-10s = %s"%(k, source[k])

###########################################################################
            
if __name__ == "__main__":
    sources = utils.get_sources()
    if len(sys.argv) == 1:
        for k in sorted([int(x) for x in sources.keys()]):
            source = sources[str(k)]
            show(source)
    else:
        update(utils.get_sources()[sys.argv[1]], sys.argv[2])
