#! /usr/bin/env python
#-*- coding: utf8 -*-

import cgi, re, sys, os
from tools import utils

def remove_bug(error_id, status):

  PgConn   = utils.get_dbconn()
  PgCursor = PgConn.cursor()

  # find source
  PgCursor.execute("SELECT source,class,subclass,elems FROM marker WHERE id = %s;",
                   (error_id, ))
  source_id = None
  for res in PgCursor.fetchall():
      source_id = res["source"]
      class_id = res["class"]
      sub_class = res["subclass"]
      elems = res["elems"]

  if not source_id:
      return -1

  ## OpenStreetBugs
  if source_id == 62:
      import commands
      s, o = commands.getstatusoutput("wget -o /dev/null -O - 'http://openstreetbugs.schokokeks.org/api/0.1/closePOIexec?id=%d'"%sub_class)
      if o.strip() <> "ok":
          print "ERROR UPDATING OpenStreetBugs"
          sys.exit(1)

  ## Other sources
  else:
      PgCursor.execute("""DELETE FROM dynpoi_status
                          WHERE source=%s AND class=%s AND subclass=%s AND elems=%s;""",
                       (source_id,class_id,sub_class,elems))
      PgCursor.execute("""INSERT INTO dynpoi_status
                          SELECT source,class,subclass,elems,NOW(),%s,
                                 subtitle->'en',lat,lon,subtitle->'fr'
                          FROM marker
                          WHERE id = %s""",
                       (status,error_id))

  PgCursor.execute("DELETE FROM marker WHERE id = %s;", (error_id, ))
  PgCursor.execute("DELETE FROM dynpoi_marker WHERE source=%s AND class=%s AND subclass=%s AND elems=%s;", (source_id, class_id, sub_class, elems))
  PgCursor.execute("DELETE FROM dynpoi_user WHERE source=%s AND class=%s AND subclass=%s AND elems=%s;", (source_id, class_id, sub_class, elems))
  PgConn.commit()

  return 0
