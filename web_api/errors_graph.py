import csv
import io
import json
import os
import sys
import tempfile
import time

from modules_legacy import query

os.environ["MPLCONFIGDIR"] = tempfile.mkdtemp()
import matplotlib

# Force matplotlib to not use any Xwindows backend.
matplotlib.use("Agg")
import matplotlib.dates
import matplotlib.pyplot


def get_data(db, params):
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
            markers.source_id,
            markers.class,
            markers.count,
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
        source_id,
        class,
        date_trunc('day', timestamp)
    ) AS t
GROUP BY
    date
ORDER BY
    date
"""

    join, where = query._build_param(
        db,
        None,
        params.source,
        params.item,
        params.level,
        None,
        params.classs,
        params.country,
        params.useDevItem,
        None,
        params.tags,
        None,
        stats=True,
        start_date=params.start_date,
        end_date=params.end_date,
    )
    where2 = ["1 = 1"]
    if params.start_date:
        where2.append("timestamp >= '%s'" % params.start_date.isoformat())
    if params.end_date:
        where2.append("timestamp < '%s'" % params.end_date.isoformat())
    where2 = " AND ".join(where2)
    sql = sqlbase % (join, where, where2)

    if len(sys.argv) > 1:
        print(sql)

    result = []
    db.execute(sql)
    for r in db.fetchall():
        result.append((r[0], r[1]))
    return result


def get_text(db, params):
    if len(params.source) == 1 and len(params.classs) == 1:
        db.execute(
            """
SELECT
    title->'en'
FROM
    markers_counts
    JOIN class ON
        class.item = markers_counts.item AND
        class.class = markers_counts.class
WHERE
    markers_counts.source_id=%s AND
    class.class=%s
""",
            (params.source[0], params.classs[0]),
        )
    elif len(params.item) == 1 and len(params.classs) == 1:
        db.execute(
            """
SELECT
    title->'en'
FROM
    class
WHERE
    class=%s AND
    item=%s
LIMIT 1
""",
            (params.classs[0], params.item[0]),
        )
    elif len(params.item) == 1:
        db.execute(
            """
SELECT
    menu->'en'
FROM
    items
WHERE
    item=%s
LIMIT 1
""",
            (params.item[0],),
        )
    else:
        return ""

    res = db.fetchone()
    if res and res[0]:
        return res[0]
    else:
        return ""


def get_src(db, params):
    ret = []
    if params.item:
        db.execute(
            "SELECT menu->'en' FROM items WHERE {0}".format(
                query._build_where_item("items", params.item)
            )
        )
        r = db.fetchone()
        if r and r[0]:
            ret.append(r[0])

    if params.item and params.classs:
        db.execute(
            "SELECT title->'en' FROM class WHERE {0} AND {1};".format(
                query._build_where_item("class", params.item),
                query._build_where_class("class", params.classs),
            )
        )
        r = db.fetchone()
        if r and r[0]:
            ret.append(r[0])

    if len(params.source) == 1:
        db.execute(
            "SELECT country, analyser FROM sources WHERE id=%s;", (params.source[0],)
        )
        r = db.fetchone()
        if r:
            ret.append(r[0])
            ret.append(r[1])

    if params.country:
        ret.append(str(params.country))

    return " - ".join(ret) if ret else "All"


def convIntsToStr(values):
    """
    Convertie une liste d'entier en chaine
    """
    return ", ".join([str(elt) for elt in values])


def make_plt(db, params, format):
    data = get_data(db, params)
    text = get_text(db, params)
    src = get_src(db, params)
    return plot(data, text + " " + src, format)


def plot(data, title, format):
    if format == "json":
        jsonData = {}
        for d in data:
            jsonData[d[0].strftime("%Y-%m-%dT%H:%M:%SZ")] = int(d[1])

        return json.dumps({"title": title, "data": jsonData})
    elif format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        h = ["timestamp", "value"]
        writer.writerow(h)
        for d in data:
            writer.writerow([d[0].strftime("%Y-%m-%dT%H:%M:%SZ"), int(d[1])])
        return output.getvalue()
    else:
        dates = [q[0] for q in data]
        opens = [q[1] for q in data]
        fig = matplotlib.pyplot.figure()
        ax = fig.add_subplot(111)
        ax.plot_date(dates, opens, "-", color="r")
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
        ax.fmt_ydata = lambda x: "$%1.2f" % x
        ax.grid(True)

        locator = matplotlib.dates.AutoDateLocator()
        formatter = matplotlib.dates.AutoDateFormatter(locator)
        formatter.scaled[30.0] = "%Y-%m"
        formatter.scaled[1.0] = "%Y-%m-%d"
        ax.xaxis.set_major_locator(locator)
        ax.xaxis.set_major_formatter(formatter)

        fig.autofmt_xdate()

        buf = io.BytesIO()
        fig.savefig(buf, format=format)
        matplotlib.pyplot.close(fig)
        return buf.getvalue()


if __name__ == "__main__":
    from optparse import OptionParser

    start = time.clock()

    parser = OptionParser()
    parser.add_option(
        "--source", dest="source", type="int", action="append", default=[]
    )
    parser.add_option("--class", dest="classs", type="int", action="append", default=[])
    parser.add_option("--item", dest="item", type="int", action="append", default=[])
    parser.add_option("--level", dest="level", type="int", action="append", default=[])
    parser.add_option("--country", dest="country", type="string", default=None)
    (options, args) = parser.parse_args()

    data = make_plt(None, options, "png")
    f = open("graph.png", "w")
    f.write(data)
    f.close()
    end = time.clock()
    print("graph.png generated in %ims" % ((end - start) * 1000))
    sys.exit(0)
