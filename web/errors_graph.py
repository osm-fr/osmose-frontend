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

import time, sys, datetime, io, os, tempfile, json, csv
from datetime import timedelta
os.environ['MPLCONFIGDIR'] = tempfile.mkdtemp()
import matplotlib
# Force matplotlib to not use any Xwindows backend.
matplotlib.use('Agg')
import matplotlib.pyplot
import matplotlib.dates
from modules.params import Params
from modules import query


def get_data(db, options):
    sqlbase = """
SELECT
    date,
    SUM(count)
FROM (
    SELECT
        date_trunc('day', timestamp) AS date,
        AVG(count) AS count
    FROM (
        SELECT
            marker.source,
            marker.class,
            marker.count,
            generate_series(
                lower(timestamp_range),
                coalesce(upper(timestamp_range) - '23 hour'::interval, now()),
                '1 day'::interval
            )::timestamp without time zone AS timestamp
        FROM
            %s
        WHERE
            %s
        ) AS t
    WHERE
        %s
    GROUP BY
        source,
        class,
        date_trunc('day', timestamp)
    ) AS t
GROUP BY
    date
ORDER BY
    date
"""

    params = Params()
    join, where = query._build_param(db, None, params.source, params.item, params.level, None, params.classs, params.country, params.useDevItem, None, params.tags, None, stats=True, start_date=params.start_date, end_date=params.end_date)
    where2 = ["1 = 1"]
    if params.start_date:
        where2.append("timestamp >= '%s'" % params.start_date.isoformat())
    if params.end_date:
        where2.append("timestamp < '%s'" % params.end_date.isoformat())
    where2 = " AND ".join(where2)
    sql = sqlbase % (join, where, where2)

    if len(sys.argv)>1:
      print(sql)

    result = []
    db.execute(sql)
    for r in db.fetchall():
        result.append((r[0],r[1]))
    return result


def get_text(db, options):
    if len(options.sources)==1 and len(options.classes)==1:
        db.execute("SELECT title->'en' FROM dynpoi_class JOIN class ON class.item = dynpoi_class.item AND class.class = dynpoi_class.class WHERE dynpoi_class.source=%s AND class.class=%s;", (options.sources[0], options.classes[0]))
    elif len(options.items)==1 and len(options.classes)==1:
        db.execute("SELECT title->'en' FROM class WHERE class=%s AND item=%s LIMIT 1;", (options.classes[0], options.items[0]))
    elif len(options.items)==1:
        db.execute("SELECT menu->'en' FROM items WHERE item=%s LIMIT 1;", (options.items[0],))
    else:
        return ""

    res = db.fetchone()
    if res and res[0]:
        return res[0]
    else:
        return ""


def get_src(db, options):
    if len(options.sources) == 1:
        db.execute("SELECT country, analyser FROM sources WHERE id=%s;", (options.sources[0], ))
        r = db.fetchone()
        return r[0] + " - " + r[1]

    elif options.country:
        return str(options.country)

    else:
        return "All"


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


class AutoDateLocatorDay(matplotlib.dates.AutoDateLocator):
    def get_locator(self, dmin, dmax):
        if dmax-dmin <= timedelta(days=5):
            return matplotlib.dates.AutoDateLocator.get_locator(self, dmax-timedelta(days=5), dmax)
        else:
            return matplotlib.dates.AutoDateLocator.get_locator(self, dmin, dmax)


def plot(data, title, format):
    if format == 'json':
        jsonData = {}
        for d in data:
            jsonData[d[0].strftime("%Y-%m-%dT%H:%M:%SZ")] = int(d[1])

        return json.dumps({
            'title': title,
            'data': jsonData
        })
    elif format == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        h = ['timestamp', 'value']
        writer.writerow(h)
        for d in data:
            writer.writerow([d[0].strftime("%Y-%m-%dT%H:%M:%SZ"), int(d[1])])
        return output.getvalue()
    else:
        dates = [q[0] for q in data]
        opens = [q[1] for q in data]
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        ax.plot_date(dates, opens, '-', color='r')
        ax.set_title(title)
        # format the ticks
        ax.relim()
        if len(opens) > 1:
            ytop = float(max(opens)) * 1.05 + 1
        else:
            ytop = None
        ax.set_ylim(bottom=0, top=ytop)
        ax.autoscale_view()
        # format the coords message box
        ax.fmt_ydata = lambda x: '$%1.2f'%x
        ax.grid(True)

        locator = AutoDateLocatorDay()
        locator.set_axis(ax.xaxis)
        locator.refresh()
        formatter = matplotlib.dates.AutoDateFormatter(locator)
        formatter.scaled[30.] = '%Y-%m'
        formatter.scaled[1.0] = '%Y-%m-%d'
        ax.xaxis.set_major_formatter(formatter)

        fig.autofmt_xdate()

        buf = io.BytesIO()
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
    parser.add_option("--level", dest="levels", type="int", action="append", default=[])
    parser.add_option("--country", dest="country", type="string", default=None)
    (options, args) = parser.parse_args()

    data = make_plt(None, options, "png")
    f = open("graph.png", "w")
    f.write(data)
    f.close()
    end = time.clock()
    print("graph.png generated in %ims"%((end-start)*1000))
    sys.exit(0)
