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

import sys, os, time, commands, cgi
from pyPgSQL import PgSQL

PgConn = PgSQL.connect(database = 'osmose', user = 'osmose')
PgCurs = PgConn.cursor()

###########################################################################
## get timestamps

def get_data(the_source, the_class, the_item):
    all = []
    if the_source == -1:
      sql =  "SELECT dynpoi_stats.source, dynpoi_stats.timestamp, SUM(dynpoi_stats.count) AS count "
      sql =  "SELECT dynpoi_stats.source, dynpoi_stats.timestamp, dynpoi_stats.count "
      sql += "FROM dynpoi_stats %s "
      sql += "WHERE 1=1 %s %s "
#      sql += "GROUP BY dynpoi_stats.source, dynpoi_stats.timestamp "
      sql += "ORDER BY timestamp;"
      if the_item == -1:
         join_item = ""
         where_item = ""
      else:
         join_item = "JOIN dynpoi_class ON dynpoi_stats.source = dynpoi_class.source AND dynpoi_stats.class = dynpoi_class.class"
         where_item = "AND dynpoi_class.item=%d" % the_item

      if the_class == -1:
         where_class = ""
      else:
         where_class = "AND dynpoi_stats.class=%d" % the_class

      sql = sql % (join_item, where_item, where_class)

      PgCurs.execute(sql)
      last = dict() 
      prev_timestamp = 0
      for res in PgCurs.fetchall():
        last[res["source"]] = res['count']
        if (res['timestamp'] - prev_timestamp) > 7*24*3600:
          sum = 0
          for v in last.itervalues():
            sum += v
          all.append((res['timestamp'].strftime('%d/%m/%Y'), sum))
          prev_timestamp = res['timestamp']
    else:
      PgCurs.execute("SELECT * FROM dynpoi_stats WHERE source=%d AND class=%d ORDER BY timestamp;"%(the_source, the_class))
      for res in PgCurs.fetchall():
        all.append((res['timestamp'].strftime('%d/%m/%Y'), res['count']))
    return all

def get_text(the_source, the_class, the_item):
    if the_source == -1:
        if the_item == -1:
            return ""
        else:
            PgCurs.execute("SELECT title_en FROM dynpoi_class WHERE class=%d AND item=%d LIMIT 1;"%(the_class, the_item))
    else:
        PgCurs.execute("SELECT title_en FROM dynpoi_class WHERE source=%d AND class=%d;"%(the_source, the_class))
    res = PgCurs.fetchone()
    if res:
        return res[0]
    else:
        return ""

def get_src(the_source):
    if the_source == -1:
        return "All"
    else:
        PgCurs.execute("SELECT comment FROM dynpoi_source WHERE source=%d;"%(the_source))
        return PgCurs.fetchone()[0]

def make_plt(the_source, the_class, the_item):
    
    data = get_data(the_source, the_class, the_item)
    text = get_text(the_source, the_class, the_item)
    
    if not data or len(data) < 2:
         raise SystemError("no data available")
    
    f_plt = open('data_%d_%d.plt'%(the_source, the_class), 'w')
    f_plt.write("set terminal png\n")
    f_plt.write("set title \"Source : %s\"\n"%get_src(the_source))
    f_plt.write("set style data fsteps\n")
    f_plt.write("set timefmt \"%d/%m/%Y\"\n")
    f_plt.write("set xdata time\n")
    f_plt.write("set xrange [ \"%s\":\"%s\" ]\n"%(data[0][0], data[-1][0]))
    f_plt.write("set format x \"%d/%m\\n%Y\"\n")
    #f_plt.write("set xlabel \"Date\nTime\"\n")
    f_plt.write("set yrange [ %d : %d ]\n"%(100*(min([x[1] for x in data])/100),100*(max([x[1] for x in data])/100+2)))
    #f_plt.write("set ylabel "Concentration\nmg/l"\n")    
    f_plt.write("set grid\n")
    f_plt.write("set key left\n")
    f_plt.write("plot 'data_%d_%d.dat' using 1:2 t '%s'\n"%(the_source, the_class, text))
    f_plt.close()
    
    f_dat = open('data_%d_%d.dat'%(the_source, the_class), 'w')
    for x in data:
        f_dat.write("%s %d\n"%(x[0], x[1]))
    f_dat.close()

    s, o = commands.getstatusoutput("gnuplot-nox data_%d_%d.plt"%(the_source, the_class))
    
    if s:
        raise SystemError("error in gnuplot generation")
    
    os.remove("data_%d_%d.plt"%(the_source, the_class))
    os.remove("data_%d_%d.dat"%(the_source, the_class))
    
    return o
    
###########################################################################

if len(sys.argv)>1:
    print "test on source %d class %d item %d"%(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    make_plt(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
    sys.exit(0)

if len(sys.argv)>1:
    the_source = int(sys.argv[1])
    the_class  = int(sys.argv[2])
    the_class  = int(sys.argv[3])
else:
    form   = cgi.FieldStorage()
    the_source = int(form.getvalue("source", "-1"))
    the_class  = int(form.getvalue("class", "-1"))
    the_item   = int(form.getvalue("item", "-1"))

try:
    data = make_plt(the_source, the_class, the_item)
    print "Content-type: image/png"
    print ""
    print data
except Exception, e:
    print "Content-type: text/plain"
    print ""
    print e

# age  = lasts[int(source_id)]["age"] # now - time.mktime(time.strptime(str(lasts[int(source_id)]["timestamp"]),"%Y-%m-%dT%H:%M:%SZ"))
