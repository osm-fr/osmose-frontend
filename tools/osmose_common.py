#! /usr/bin/env python
#-*- coding: utf8 -*-

import cgi, re, sys, os
from tools import utils

def remove_bug(source_id, class_id, sub_class, elems, status):

  PgConn   = utils.get_dbconn()
  PgCursor = PgConn.cursor()

  ## OpenStreetBugs
  if source_id==62:
    import commands
    s, o = commands.getstatusoutput("wget -o /dev/null -O - 'http://openstreetbugs.schokokeks.org/api/0.1/closePOIexec?id=%d'"%sub_class)
    if o.strip() <> "ok":
      return -1

  ## Other sources
  else:
    PgCursor.execute("""DELETE FROM dynpoi_status
                        WHERE source=%s AND class=%s AND subclass=%s AND elems=%s""",
                     (source_id, class_id, sub_class, elems))
    PgCursor.execute("""INSERT INTO dynpoi_status (source,class,subclass,elems,date,status) VALUES
                                                (%s,%s,%s,%s,NOW(),%s)""",
                     (source_id, class_id, sub_class, elems, status))
    
  #PgCursor.execute("DELETE FROM dynpoi_marker WHERE (source,class,subclass,elems) IN (SELECT source,class,subclass,elems FROM dynpoi_status);")
  PgCursor.execute("""DELETE FROM dynpoi_marker
                      WHERE source=%s AND class=%s AND subclass=%s AND elems=%s""",
                   (source_id, class_id, sub_class, elems))
  PgConn.commit()

  return 0
