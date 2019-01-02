#! /usr/bin/env python
#-*- coding: utf-8 -*-

import cgi, re, sys, os
from tools import utils

def remove_bug(error_id, status):

  PgConn   = utils.get_dbconn()
  PgCursor = PgConn.cursor()

  # find source
  PgCursor.execute("SELECT source,class,subclass,elems,lat,lon FROM marker WHERE id = %s;",
                   (error_id, ))
  source_id = None
  for res in PgCursor.fetchall():
      source_id = res["source"]
      class_id = res["class"]
      sub_class = res["subclass"]
      elems = res["elems"]
      lat = res["lon"]
      lon = res["lat"]

  if not source_id:
      return -1

  if len(elems) > 1:
    PgCursor.execute("""DELETE FROM dynpoi_status
                        WHERE source=%s AND class=%s AND subclass=%s AND elems=%s;""",
                     (source_id,class_id,sub_class,elems))
  else:
    PgCursor.execute("""DELETE FROM dynpoi_status
                        WHERE source=%s AND class=%s AND subclass=%s AND lat=%s AND lon=%s;""",
                     (source_id,class_id,sub_class,lat,lon))
  PgCursor.execute("""INSERT INTO dynpoi_status
                        (id,source,class,subclass,elems,date,status,lat,lon,subtitle)
                      SELECT id,source,class,subclass,elems,NOW(),%s,
                             lat,lon,subtitle
                      FROM marker
                      WHERE id = %s
                      ON CONFLICT DO NOTHING""",
                   (status,error_id))

  PgCursor.execute("DELETE FROM marker WHERE id = %s;", (error_id, ))
  PgCursor.execute("UPDATE dynpoi_class SET count = count - 1 WHERE source = %s AND class = %s;", (source_id, class_id))
  PgConn.commit()

  return 0
