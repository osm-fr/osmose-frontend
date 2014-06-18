#!/usr/bin/env python
#-*- coding: utf-8 -*-

all_flags = ["O", "L", "K", "P", "M", "F", "=", "|", "||", "::", ".:.", "T", "t", "X", "><", "L'", "[]", ".", ".l", "'.", "/", "=-"]

import utils

if __name__ == "__main__":

  dbconn = utils.get_dbconn()
  dbcurs = dbconn.cursor()

  sql = "select marker.item from marker left join dynpoi_item on dynpoi_item.item = marker.item where dynpoi_item.item IS NULL group by marker.item order by marker.item;"
  dbcurs.execute(sql)

  prev_cat = ""

  for res in dbcurs.fetchall():
  #  print res
    i = int(res[0])
    c = int(i / 1000) * 10
    if prev_cat != c:
        prev_cat = c
        avail_flags = all_flags[:]

    sql = "select item, marker_color, marker_flag from dynpoi_item where categ = %s order by item"
    dbcurs.execute(sql, (c,))
    for m in dbcurs.fetchall():
  #    print m
      color = m["marker_color"]
      if m["marker_flag"] in avail_flags:
        avail_flags.remove(m["marker_flag"])

  #  print "  missing %d" % i
  #  print "possible flags:", avail_flags

    if len(avail_flags) == 0:
      print "not enough available flags for item=%d" % i
      continue

  #  en = raw_input("English: ")
  #  fr = raw_input("French: ")

    print "insert into dynpoi_item values (%d, %d, '%s', '%s', NULL, ARRAY[1, 2, 3]);" % (i, c, color, avail_flags[0].replace("'", "''"))
    avail_flags.remove(avail_flags[0])

