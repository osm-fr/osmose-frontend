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
import datetime
import utils
from xml.sax import make_parser, handler
translate = utils.translator()._data
tpl = open(os.path.join(utils.root_folder, "config/text.tpl")).read()

###########################################################################
## logger

class printlogger:
    def log(self, text):
        print text


def get_date(ts):
  return datetime.datetime.strptime(ts, "%Y-%m-%d %H:%M:%S.00").date()
###########################################################################
## updater

def update(source, o, logger = printlogger()):
    
    source_id = int(source["id"])
        
    ## open connections
    dbconn = utils.get_dbconn()
    dbcurs = dbconn.cursor()
    
    ## xml parser
    parser = make_parser()
    parser.setContentHandler(update_parser(source_id, source, dbcurs, o))

    dbcurs.execute("SELECT remote_url from dynpoi_update u join dynpoi_update_last l on u.source = l.source and u.timestamp = l.timestamp where l.source = %d" % int(source["id"]))
    url = [x[0] for x in dbcurs.fetchall()][0]
        
    ## download the file if needed
    if url.startswith("http://"):
        fname =  tempfile.mktemp()
        urllib.urlretrieve(url, fname)
        #mysock = urllib.urlopen(source["url"])
        #open(fname,'w').write(mysock.read())
        istemp = True
    else:
        return
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
        
    o.write("<html>\n")
    o.write("<head>\n")
    o.write("<title>Statistiques pour %s</title>\n" % source["comment"])
    o.write("<link rel='stylesheet' type='text/css' href='style.css' />\n")
    o.write("</head>\n")

    o.write("<body>\n")
    o.write("<h1>Statistiques pour %s</h1>\n" % source["comment"])

    ## parse the file
    parser.parse(f)

    o.write("</body>\n")
    o.write("</html>\n")
    

    ## commit and close
    dbconn.commit()
    dbconn.close()
    
    ## close and delete
    f.close()
    del f
    if istemp:
        os.remove(fname)

class update_parser(handler.ContentHandler):
    
    def __init__(self, source_id, source_data, dbcurs, output):
        self._source_id        = source_id
        self._source_data      = source_data
        self._dbcurs           = dbcurs
        self._class_texts      = {}
        self._class_item       = {}
        self._copy_marker_name = tempfile.mktemp()
        self._copy_marker      = open(self._copy_marker_name, 'w')
        self._copy_user_name   = tempfile.mktemp()
        self._copy_user        = open(self._copy_user_name, 'w')
        self.o                 = output
        
    def startElement(self, name, attrs):
        if name == u"analyser":
            ts = datetime.datetime.strptime(attrs["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            self.o.write((u"<div style='font-weight: bold'>Mise à jour du %s %s</div><br>" % (ts.date(), ts.time())).encode("utf-8"))

            for t in ["nodes", "ways", "relations"]:
                self.o.write("<a href='#users_%s'>Utilisateurs par %s</a><br>" % (t, t))

        elif name == u"stat_users":
            self._stat_type       = attrs["type"]
            self._stat_all        = []

        elif name == u"user":
            self._stat_user       = {}
            self._stat_user["name"]  = attrs["user_name"]
            self._stat_user["id"]    = attrs["user_id"]
        elif name == u"count":
            self._stat_user["count"] = attrs["value"]
        elif name == u"timestamp":
            self._stat_user["min_timestamp"] = get_date(attrs["min"])
            self._stat_user["max_timestamp"] = get_date(attrs["max"])
            
    def endElement(self, name):
        if name == "analyser":
            pass

        elif name == u"stat_users":
            self.o.write("<h3><a name='users_%s'></a>Statistiques par utilisateurs pour les %s</h3>" % (self._stat_type, self._stat_type))
            self.o.write("<table>\n")
            self.o.write("  <tr>\n")
            keys = ["id", "name", "count", "min_timestamp", "max_timestamp"]
            for k in keys:
                self.o.write("  <th>%s</th>\n" % k)
            self.o.write("  </tr>\n")

            num = 0
            for u in self._stat_all:
                num += 1
#                if num > 40:
#                   break
                if int(u["count"]) < 10:
                    break

                self.o.write("  <tr>\n")
                for k in keys:
                    style=''
                    if k == "max_timestamp": 
                        if u[k] < datetime.date.fromtimestamp(time.time() - 60*24*3600):
                            style = 'bad'
                        if u[k] > datetime.date.fromtimestamp(time.time() - 7*24*3600):
                            style = 'good'

                    if k == "min_timestamp": 
                        if u[k] < datetime.date.fromtimestamp(time.time() - 60*24*3600):
                            style = 'good'
                        if u[k] > datetime.date.fromtimestamp(time.time() - 7*24*3600):
                            style = 'bad'

                    self.o.write((u"  <td class='%s'>%s</td>" % (style, u[k])).encode("utf-8"))
                self.o.write("  </tr>\n")
            self.o.write("</table>\n")

        elif name == u"user":
            self._stat_all.append(self._stat_user)
            
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
    if len(sys.argv) > 1:
        try:
            num = int(sys.argv[1])
        except ValueError:
           for k in sorted([int(x) for x in sources.keys()]):
                source = sources[str(k)]
                if source["comment"].startswith("stats-"):
                    print source
                    show(source)

           sys.exit(1)

        else:
            sources = {sys.argv[1]: sources[sys.argv[1]]}

    for k, source in sources.iteritems():
        if source["comment"].startswith("stats-"):
            print source["comment"]
            filename = os.path.join(utils.root_folder, "website", "stats", source["comment"] + ".html")
            f = open(filename, "w")
            update(source, f)
