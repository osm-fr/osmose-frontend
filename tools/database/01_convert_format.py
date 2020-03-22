#! /usr/bin/env python
#-*- coding: utf-8 -*-

import cgi, re, sys, os, psycopg2.extras
import utils


conn = utils.get_dbconn()
#psycopg2.extras.register_hstore(conn, globally=True, oid=1408668)
#psycopg2.extras.register_hstore(conn)
cur = conn.cursor("1")
cur_mod = conn.cursor()

sql = """
SELECT m.source, m.class, m.subclass, m.lat, m.lon, m.item,
       m.subtitle_en, m.subtitle_fr, m.elems, m.data
FROM dynpoi_marker m
"""

cur.execute(sql)

num_err = 0
many_res = cur.fetchmany(1000)

while many_res:
  print(num_err, "\r", end=' ')
  sys.stdout.flush()
  num_err += 1000
  for res in many_res:

    sql_marker = """
INSERT INTO marker (source,class,subclass,lat,lon,elems,item,subtitle)
         VALUES (%s, %s, %s, %s, %s, %s, %s, %s)  RETURNING id;
"""
    sql_elem = """
INSERT INTO marker_elem (marker_id, elem_index, data_type, id, tags, username)
         VALUES (%s, %s, %s, %s, %s, %s);
"""
    cur_mod.execute(sql_marker, (res["source"], res["class"], res["subclass"], res["lat"], res["lon"],
                                 res["elems"], res["item"],
                                 { "en": res["subtitle_en"], "fr": res["subtitle_fr"]}))
    err_id = cur_mod.fetchone()[0]
#    print err_id

    elems = []
    if res["data"]:
      for i in range(len(res["data"])/2):
        if res["data"][2*i].startswith("##"):
          elems.append([res["data"][2*i][2:], res["data"][2*i+1], {}])
        else:
          elems[-1][2][res["data"][2*i]] = res["data"][2*i+1]
    num = 0
    for e in elems:
      if e[0] == "infos":
        elm_id = 0
        elm_tags = e[2]
        elm_tags["infos"] = e[1]
      else:
        elm_id = int(e[1])
        elm_tags = e[2]
#      print sql_elem, (err_id, num, e[0][0].upper(), elm_id, elm_tags, None)
#      print cur_mod.mogrify(sql_elem, (err_id, num, e[0][0].upper(), elm_id, elm_tags, None))
      cur_mod.execute(sql_elem, (err_id, num, e[0][0].upper(), elm_id, elm_tags, None))
      num += 1

  many_res = cur.fetchmany(1000)


cur_mod.execute("drop view dynpoi_update_last")
cur_mod.execute("""create table dynpoi_update_last as ( SELECT dynpoi_update.source, max(dynpoi_update."timestamp") AS "timestamp"
   FROM dynpoi_update
  GROUP BY dynpoi_update.source)""")
cur_mod.execute("alter table dynpoi_update_last add primary key (source)")

conn.commit()

