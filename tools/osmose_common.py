#! /usr/bin/env python
#-*- coding: utf-8 -*-

import cgi, re, sys, os
from tools import utils

def remove_bug_err_id(error_id, status):

  PgConn   = utils.get_dbconn()
  PgCursor = PgConn.cursor()

  # find source
  PgCursor.execute("SELECT source,class,subclass,elems,lat,lon FROM marker WHERE id = %s", (error_id, ))
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

  PgCursor.execute("DELETE FROM dynpoi_status WHERE marker_id=%s", (error_id, ))

  PgCursor.execute("""INSERT INTO dynpoi_status
                        (id,source,class,subclass,elems,date,status,lat,lon,subtitle,uuid)
                      SELECT id,source,class,subclass,elems,NOW(),%s,
                             lat,lon,subtitle,uuid
                      FROM marker
                      WHERE id = %s
                      ON CONFLICT DO NOTHING""",
                   (status, error_id))

  PgCursor.execute("DELETE FROM marker WHERE id = %s", (error_id, ))
  PgCursor.execute("UPDATE dynpoi_class SET count = count - 1 WHERE source = %s AND class = %s;", (source_id, class_id))
  PgConn.commit()

  return 0


def remove_bug_uuid(uuid, status):

  PgConn   = utils.get_dbconn()
  PgCursor = PgConn.cursor()

  # find source
  PgCursor.execute("SELECT source,class,subclass,elems,lat,lon FROM marker WHERE uuid = %s", (uuid, ))
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

  PgCursor.execute("DELETE FROM dynpoi_status WHERE uuid=%s", (uuid, ))

  PgCursor.execute("""INSERT INTO dynpoi_status
                        (id,source,class,subclass,elems,date,status,lat,lon,subtitle,uuid)
                      SELECT id,source,class,subclass,elems,NOW(),%s,
                             lat,lon,subtitle,uuid
                      FROM marker
                      WHERE uuid = %s
                      ON CONFLICT DO NOTHING""",
                   (status, uuid))

  PgCursor.execute("DELETE FROM marker WHERE uuid = %s", (uuid, ))
  PgCursor.execute("UPDATE dynpoi_class SET count = count - 1 WHERE source = %s AND class = %s;", (source_id, class_id))
  PgConn.commit()

  return 0
