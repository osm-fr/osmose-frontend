#!/usr/bin/env python3
#-*- coding: utf-8 -*-

all_flags = ["O", "L", "K", "P", "M", "F", "=", "|", "||", "::", ".:.", "T", "t", "X", "><", "L'", "[]", ".", ".l", "'.", "/", "=-", "H", "h"]

import pprint
from modules import utils

if __name__ == "__main__":

  dbconn = utils.get_dbconn()
  dbcurs = dbconn.cursor()

  sql = """
CREATE TEMP TABLE marker_list_item AS
WITH RECURSIVE t AS (
   (SELECT item FROM markers ORDER BY item LIMIT 1)  -- parentheses required
   UNION ALL
   SELECT (SELECT item FROM markers WHERE item > t.item ORDER BY item LIMIT 1)
   FROM t
   WHERE t.item IS NOT NULL
   )
SELECT item FROM t WHERE item IS NOT NULL;
"""
  dbcurs.execute(sql)

  sql = """
select m.item 
from marker_list_item m
left join items on items.item = m.item
where items.item IS NULL
order by m.item;"""
  dbcurs.execute(sql)

  prev_cat = ""

  for res in dbcurs.fetchall():
  #  print res
    item = int(res[0])
    categ = int(item / 1000) * 10

    if prev_cat != categ:
      prev_cat = categ
      colors = set()
      avail_flags = {}
      sql = "select item, marker_color, marker_flag from items where categorie_id = %s order by item"
      dbcurs.execute(sql, (categ,))
      for m in dbcurs.fetchall():
        color = m["marker_color"]
        colors.add(color)
        if color not in avail_flags:
          avail_flags[color] = all_flags[:]
        if m["marker_flag"] in avail_flags[color]:
          avail_flags[color].remove(m["marker_flag"])

    chosen_color = None
    chosen_flag = None
    for c in colors:
      if len(avail_flags[c]) > 0:
        chosen_color = c
        chosen_flag = avail_flags[c][0]
        continue

    if not chosen_color:
      print("not enough available flags for item=%d" % item)
      continue

    print("insert into items values (%d, %d, '%s', '%s', NULL, ARRAY[1, 2, 3]);" % (item, categ, chosen_color, chosen_flag.replace("'", "''")))
    avail_flags[chosen_color].remove(chosen_flag)

