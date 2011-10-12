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
    all = []
    sql =  "SELECT dynpoi_stats.source, dynpoi_stats.class, dynpoi_stats.timestamp, dynpoi_stats.count "
    sql += "FROM dynpoi_stats %s "
    sql += "WHERE 1=1 %s "
    sql += "ORDER BY timestamp"

    join_item = ""
    where_sql = ""

    if options.item >= 0:
       join_item += "JOIN dynpoi_class ON dynpoi_stats.source = dynpoi_class.source AND dynpoi_stats.class = dynpoi_class.class "
       where_sql += "AND dynpoi_class.item=%d " % options.item

    if options.classe >= 0:
       where_sql += "AND dynpoi_stats.class=%d " % options.classe

    if options.source >= 0:
       where_sql += "AND dynpoi_stats.source=%d " % options.source

    if options.country:
       join_item += "JOIN dynpoi_source ON dynpoi_stats.source = dynpoi_source.source "
       where_sql += "AND dynpoi_source.comment LIKE '%%-%s%%' " % options.country

    sql = sql % (join_item, where_sql)

    if len(sys.argv)>1:
      print sql

    PgCurs.execute(sql)

    if options.source == -1:
      delay = 4*24*3600
    else:
      delay = 1

    last = dict()
    timestamp = 0
    prev_timestamp = 0
    for res in PgCurs.fetchall():
      timestamp = res['timestamp']
      if prev_timestamp == 0:
          prev_timestamp = timestamp

      last[str(res["source"]) + "-" + str(res["class"])] = res['count']
      if (timestamp - prev_timestamp) > delay:
        sum = 0
        for v in last.itervalues():
          sum += v
        all.append((prev_timestamp.strftime('%d/%m/%Y'), sum))
        prev_timestamp = timestamp

    sum = 0
    for v in last.itervalues():
      sum += v
    if timestamp == 0:
      return []
    all.append((timestamp.strftime('%d/%m/%Y'), sum))
     
    return all

def get_text(options):
    if options.source == -1:
        if options.item == -1:
            return ""
        else:
            PgCurs.execute("SELECT title_en FROM dynpoi_class WHERE class=%d AND item=%d LIMIT 1;"%(options.classe, options.item))
    else:
        PgCurs.execute("SELECT title_en FROM dynpoi_class WHERE source=%d AND class=%d;"%(options.source, options.classe))
    res = PgCurs.fetchone()
    if res:
        return res[0]
    else:
        return ""

def get_src(options):
    if options.source == -1:
        return "All"
    else:
        PgCurs.execute("SELECT comment FROM dynpoi_source WHERE source=%d;"%(options.source))
        return PgCurs.fetchone()[0]

def make_plt(options):
    
    data = get_data(options)
    text = get_text(options)
    
    if not data or len(data) < 2:
         raise SystemError("no data available")
    
    f_plt = open('/tmp/data_%d_%d.plt'%(options.source, options.classe), 'w')
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
    f_plt.write("plot '/tmp/data_%d_%d.dat' using 1:2 t '%s'\n"%(options.source, options.classe, text))
    f_plt.close()
    
    f_dat = open('/tmp/data_%d_%d.dat'%(options.source, options.classe), 'w')
    for x in data:
        f_dat.write("%s %d\n"%(x[0], x[1]))
    f_dat.close()

    s, o = commands.getstatusoutput("gnuplot-nox /tmp/data_%d_%d.plt"%(options.source, options.classe))
    
    if s:
        raise SystemError("error in gnuplot generation")
    
    os.remove("/tmp/data_%d_%d.plt"%(options.source, options.classe))
    os.remove("/tmp/data_%d_%d.dat"%(options.source, options.classe))
    
    return o
    
###########################################################################

if len(sys.argv)>1:
    from optparse import OptionParser, SUPPRESS_HELP

    parser = OptionParser()

    parser.add_option("--source", dest="source", type="int", default=-1)
    parser.add_option("--class", dest="classe", type="int", default=-1)
    parser.add_option("--item", dest="item", type="int", default=-1)
    parser.add_option("--country", dest="country", type="string", default=None)
    (options, args) = parser.parse_args()

    data = make_plt(options)
    f = open("graph.png", "w")
    f.write(data)
    f.close()
    sys.exit(0)

else:
    form   = cgi.FieldStorage()
    class options:
      source  = int(form.getvalue("source", "-1"))
      classe  = int(form.getvalue("class", "-1"))
      item    = int(form.getvalue("item", "-1"))
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
