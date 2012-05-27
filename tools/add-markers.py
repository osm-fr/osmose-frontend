#!/usr/bin/env python
#-*- coding: utf-8 -*-

all_flags = ["O", "L", "K", "P", "M", "F", "=", "|", "||", "::", ".:.", "T", "t", "X", "><", "L''", "[]", "."]

from pyPgSQL import PgSQL

gisconn = PgSQL.Connection("dbname=%s user=%s password=%s" % ("osmose", "osmose", "-osmose-"))
giscurs = gisconn.cursor()

sql = "select marker.item from marker left join dynpoi_item on dynpoi_item.item = marker.item where dynpoi_item.item IS NULL group by marker.item order by marker.item;"
giscurs.execute(sql)

prev_cat = ""

for res in giscurs.fetchall():
  print res
  i = int(res[0])
  c = int(i / 1000) * 10
  if prev_cat != c:
      prev_cat = c
      avail_flags = all_flags[:]

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

#  en = raw_input("English: ")
#  fr = raw_input("French: ")

  print "insert into dynpoi_item values (%d, %d, '', '', '%s', '%s');" % (i, c, color, avail_flags[0])
  avail_flags.remove(avail_flags[0])

