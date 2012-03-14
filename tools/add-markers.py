#!/usr/bin/env python
#-*- coding: utf-8 -*-

all_flags = ["O", "L", "K", "P", "M", "F", "=", "|", "||", "::", ".:.", "T", "t", "X", "><", "L'", "[]", "."]

from pyPgSQL import PgSQL

gisconn = PgSQL.Connection("dbname=%s user=%s password=%s" % ("osmose", "osmose", "-osmose-"))
giscurs = gisconn.cursor()

sql = "select dynpoi_marker.item from dynpoi_marker left join dynpoi_item on dynpoi_item.item = dynpoi_marker.item where dynpoi_item.item IS NULL group by dynpoi_marker.item order by dynpoi_marker.item;"
giscurs.execute(sql)

for res in giscurs.fetchall():
  print res
  avail_flags = all_flags[:]

  i = int(res[0])
  c = int(i / 1000) * 10
  sql = "select item, marker_color, marker_flag from dynpoi_item where categ = %s"
  giscurs.execute(sql, (c,))
  for m in giscurs.fetchall():
    print m
    color = m["marker_color"]
    if m["marker_flag"] in avail_flags:
      avail_flags.remove(m["marker_flag"])

  print "  missing %d" % i
  print "possible flags:", avail_flags

  if len(avail_flags) == 0:
    print "not enough available flags"
    continue

  en = raw_input("English: ")
  fr = raw_input("French: ")

  print "insert into dynpoi_item values (%d, %d, '%s', '%s', '%s', '%s');" % (i, c, en, fr, color, avail_flags[0])
  avail_flags.remove(avail_flags[0])

