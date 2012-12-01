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

import time, sys, datetime, StringIO, os, tempfile
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot
import matplotlib.dates


def get_data(db, options):
    sql = """
SELECT
    date,
    SUM(count)
FROM (
SELECT
    date_trunc('day', dynpoi_stats.timestamp) AS date,
    AVG(dynpoi_stats.count) AS count
FROM
    dynpoi_stats
    %s
WHERE 1=1
    %s
GROUP BY
    dynpoi_stats.source,
    dynpoi_stats.class,
    date
) AS t
GROUP BY
    date
ORDER BY
    date
"""

    join_item = ""
    where_sql = ""

    if len(options.items)>=1:
        join_item += """
    JOIN dynpoi_class ON
        dynpoi_stats.source = dynpoi_class.source AND
        dynpoi_stats.class = dynpoi_class.class AND
        dynpoi_class.item in (%s)
        """ % convIntsToStr(options.items)

    if len(options.classes)>=1:
        where_sql += "AND dynpoi_stats.class in (%s) " % convIntsToStr(options.classes)

    if len(options.sources)>=1:
        where_sql += "AND dynpoi_stats.source in (%s) " % convIntsToStr(options.sources)

    if options.country:
        join_item += """
    JOIN dynpoi_source ON
        dynpoi_stats.source = dynpoi_source.source AND
        dynpoi_source.comment LIKE '%%-%s%%'
        """ % options.country

    sql = sql % (join_item, where_sql)

    if len(sys.argv)>1:
      print sql

    result = []
    db.execute(sql)
    for r in db.fetchall():
        result.append((r[0],r[1]))
    return result


def get_text(db, options):
    if len(options.sources)==1 and len(options.classes)==1:
        db.execute("SELECT title->'en' FROM dynpoi_class WHERE source=%s AND class=%s;", (options.sources[0], options.classes[0]))
    elif len(options.items)==1 and len(options.classes)==1:
        db.execute("SELECT title->'en' FROM dynpoi_class WHERE class=%s AND item=%s LIMIT 1;", (options.classes[0], options.items[0]))
    elif len(options.items)==1:
        db.execute("SELECT menu->'en' FROM dynpoi_item WHERE item=%s LIMIT 1;", (options.items[0],))
    else:
        return ""

    res = db.fetchone()
    if res:
        return res[0]
    else:
        return ""


def get_src(db, options):
    if len(options.sources) != 1:
        return "All"
    else:
        db.execute("SELECT comment FROM dynpoi_source WHERE source=%s;", (options.sources[0], ))
        return db.fetchone()[0]


def convIntsToStr(values):
    """
    Convertie une liste d'entier en chaine
    """
    return ", ".join([str(elt) for elt in values])


def make_plt(db, options, format):
    data = get_data(db, options)
    text = get_text(db, options)
    src = get_src(db, options)
    return plot(data, text+' '+src, format)


def plot(data, title, format):
    dates = [q[0] for q in data]
    opens = [q[1] for q in data]

    fig = matplotlib.pyplot.figure()
    ax = fig.add_subplot(111)
    ax.plot_date(dates, opens, '-', color='r')
    ax.set_title(title)
    # format the ticks
    ax.autoscale_view()
    # format the coords message box
    ax.fmt_ydata = lambda x: '$%1.2f'%x
    ax.grid(True)

    locator = matplotlib.dates.AutoDateLocator()
    locator.set_axis(ax.xaxis)
    locator.refresh()
    formatter = matplotlib.dates.AutoDateFormatter(locator)
    formatter.scaled[30.] = '%Y-%m'
    formatter.scaled[1.0] = '%Y-%m-%d'
    ax.xaxis.set_major_formatter(formatter)

    fig.autofmt_xdate()

    buf = StringIO.StringIO()
    fig.savefig(buf, format = format)
    matplotlib.pyplot.close(fig)
    return buf.getvalue()


if __name__ == "__main__":
    from optparse import OptionParser, SUPPRESS_HELP
    start = time.clock()

    parser = OptionParser()
    parser.add_option("--source", dest="sources", type="int", action="append", default=[])
    parser.add_option("--class", dest="classes", type="int", action="append", default=[])
    parser.add_option("--item", dest="items", type="int", action="append", default=[])
    parser.add_option("--country", dest="country", type="string", default=None)
    (options, args) = parser.parse_args()

    data = make_plt(None, options)
    f = open("graph.png", "w")
    f.write(data)
    f.close()
    end = time.clock()
    print "graph.png generated in %ims"%((end-start)*1000)
    sys.exit(0)
