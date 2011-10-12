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

## ./do.py && gnuplot-nox data_62_1.plt > /data/project/http/test.png

###########################################################################
## database connection

import sys, os, time, commands, cgi, re
from pyPgSQL import PgSQL

import cgitb
cgitb.enable()

PgConn = PgSQL.connect(database = 'osmose', user = 'osmose')
PgCurs = PgConn.cursor()

###########################################################################
## get timestamps

def get_data(options):
    sql =  "SELECT dynpoi_stats.source, dynpoi_stats.class, dynpoi_stats.timestamp, dynpoi_stats.count "
    sql += "FROM dynpoi_stats %s "
    sql += "WHERE 1=1 %s "
    sql += "ORDER BY timestamp"

    join_item = ""
    where_sql = ""

    if len(options.items)==1:
       join_item += "JOIN dynpoi_class ON dynpoi_stats.source = dynpoi_class.source AND dynpoi_stats.class = dynpoi_class.class "
       where_sql += "AND dynpoi_class.item=%d " % options.items[0]
    elif len(options.items)>=1:
       join_item += "JOIN dynpoi_class ON dynpoi_stats.source = dynpoi_class.source AND dynpoi_stats.class = dynpoi_class.class "
       where_sql += "AND dynpoi_class.item in (%s) " % convIntsToStr(options.items)

    if len(options.classes)==1:
       where_sql += "AND dynpoi_stats.class=%d " % options.classes[0]
    elif len(options.classes)>=1:
       where_sql += "AND dynpoi_stats.class in (%s) " % convIntsToStr(options.classes)

    if len(options.sources)==1:
       where_sql += "AND dynpoi_stats.source=%d " % options.sources[0]
    elif len(options.sources)>=1:
       where_sql += "AND dynpoi_stats.source in (%s) " % convIntsToStr(options.sources)

    if options.country:
       join_item += "JOIN dynpoi_source ON dynpoi_stats.source = dynpoi_source.source "
       where_sql += "AND dynpoi_source.comment LIKE '%%-%s%%' " % options.country

    sql = sql % (join_item, where_sql)

    if len(sys.argv)>1:
      print sql

    PgCurs.execute(sql)

    if len(options.sources)!=1: 
        delay = 1*24*3600
    else:
        delay = 1
    
    result = []
    last = {}
    timestamp = 0
    prev_timestamp = 0
    for res in PgCurs.fetchall():
        timestamp = res['timestamp']
        if prev_timestamp == 0:
            prev_timestamp = timestamp
        
        last[(res["source"],res["class"])] = res['count']
        if (timestamp - prev_timestamp) > delay:
            result.append((timestamp.strftime('%d/%m/%Y'), sum(last.itervalues())))
            prev_timestamp = timestamp

    if last:
        result.append((timestamp.strftime('%d/%m/%Y'), sum(last.itervalues())))
    return result

def get_text(options):
    if len(options.sources)==1 and len(options.classes)==1:
        PgCurs.execute("SELECT title_en FROM dynpoi_class WHERE source=%d AND class=%d;"%(options.sources[0], options.classes[0]))
        
    elif len(options.items)==1 and len(options.classes)==1:
        PgCurs.execute("SELECT title_en FROM dynpoi_class WHERE class=%d AND item=%d LIMIT 1;"%(options.classes[0], options.items[0]))
        
    else:
        return ""
    
    res = PgCurs.fetchone()
    if res:
        return res[0]
    else:
        return ""

def get_src(options):
    if len(options.sources) != 1:
        return "All"
    else:
        PgCurs.execute("SELECT comment FROM dynpoi_source WHERE source=%d;"%(options.sources[0]))
        return PgCurs.fetchone()[0]

def make_plt(options):
    
    data = get_data(options)
    text = get_text(options)
    
    if not data or len(data) < 2:
         raise SystemError("no data available")
    
    gnuplotFilename = "/tmp/data_%i.plt"%os.getpid()
    dataFilename = "/tmp/data_%i.dat"%os.getpid()

    f_plt = open(gnuplotFilename, 'w')
    f_plt.write("set terminal png\n")
    f_plt.write("set title \"Source : %s\"\n"%get_src(options))
#    f_plt.write("set style data fsteps\n")
    f_plt.write("set style data line\n")
    f_plt.write("set timefmt \"%d/%m/%Y\"\n")
    f_plt.write("set xdata time\n")
    f_plt.write("set xrange [ \"%s\":\"%s\" ]\n"%(data[0][0], data[-1][0]))
    f_plt.write("set format x \"%d/%m\\n%Y\"\n")
    #f_plt.write("set xlabel \"Date\nTime\"\n")
    f_plt.write("set yrange [ %d : %d ]\n"%(0,100*(max([x[1] for x in data])/100+2)))
    #f_plt.write("set ylabel "Concentration\nmg/l"\n")    
    f_plt.write("set grid\n")
    f_plt.write("set key left\n")
    f_plt.write("plot '%s' using 1:2 t '%s'\n"%(dataFilename, text))
    f_plt.close()
    
    f_dat = open(dataFilename, 'w')
    for x in data:
        f_dat.write("%s %d\n"%(x[0], x[1]))
    f_dat.close()

    s, o = commands.getstatusoutput("gnuplot-nox "+gnuplotFilename)
    
    if s:
        raise SystemError("error in gnuplot generation")
    
    os.remove(gnuplotFilename)
    os.remove(dataFilename)
    
    return o
    
    
def convStrToInts(string):
    """
    Convertie une chaine en liste d'entier
    """
    string = string.replace(" ", "")
    if string=="":
        return []
    else:
        return [int(elt) for elt in string.split()]
    
def convIntsToStr(values):
    """
    Convertie une liste d'entier en chaine
    """
    return ", ".join([str(elt) for elt in values]) 
        
###########################################################################

if len(sys.argv)>1:
    from optparse import OptionParser, SUPPRESS_HELP
    start = time.clock()

    parser = OptionParser()

    parser.add_option("--source", dest="sources", type="int", action="append", default=[])
    parser.add_option("--class", dest="classes", type="int", action="append", default=[])
    parser.add_option("--item", dest="items", type="int", action="append", default=[])
    parser.add_option("--country", dest="country", type="string", default=None)
    (options, args) = parser.parse_args()

    data = make_plt(options)
    f = open("graph.png", "w")
    f.write(data)
    f.close()
    end = time.clock()
    print "graph.png generated in %ims"%((end-start)*1000)
    sys.exit(0)

else:
    form   = cgi.FieldStorage()
    class options:
      sources = convStrToInts(form.getvalue("source"))
      classes = convStrToInts(form.getvalue("class"))
      items   = convStrToInts(form.getvalue("item"))
      country = form.getvalue("country", None)
      if country <> None and not re.match(r"^([a-z_]+)$", country):
        country = None


try:
    data = make_plt(options)
    print "Content-type: image/png"
    print ""
    print data
except Exception, e:
    print "Content-type: text/plain"
    print ""
    print e


# age  = lasts[int(source_id)]["age"] # now - time.mktime(time.strptime(str(lasts[int(source_id)]["timestamp"]),"%Y-%m-%dT%H:%M:%SZ"))
