#! /usr/bin/python

import os
import sys
import utils

if __name__ == "__main__":

  dbconn = utils.get_dbconn()
  dbcurs = dbconn.cursor()

  dbcurs.execute("SELECT max(source)+1 FROM dynpoi_source;")
  for res in dbcurs.fetchall():
    source = res[0]

  def update_pass(comment, update, contact="Jocelyn Jaubert <jocelyn@osm1.crans.org>"):
    global source

    try:
      dbcurs.execute("SELECT source, comment, update FROM dynpoi_source WHERE comment=%s;",
                     (comment, ))
      if dbcurs.rowcount == 1:
        prev_update = dbcurs.fetchone()["update"]
        if prev_update == update:
          return

      # try to update password for an analyse
      dbcurs.execute("UPDATE dynpoi_source SET update=%s WHERE comment=%s;",
                     (update, comment))
    except PgSQL.OperationalError:
      print "failure on comment=%s update=%s" % (comment, update)
      return
    except:
      print "failure on comment=%s update=%s" % (comment, update)
      raise

    if dbcurs.rowcount == 0:
  #    # try to update name for an analyse for a given password
  #    dbcurs.execute("UPDATE dynpoi_source SET comment=%s WHERE update=%s;",
  #                   (comment, update))
      pass
    else:
      print "updated update=%s where comment=%s" % (update, comment)
      return

    if dbcurs.rowcount == 0:
      # otherwise, create a new entry in database
      print "inserting comment=%s source=%s update=%s" % (comment, source, update)
      try:
        dbcurs.execute("INSERT INTO dynpoi_source (update, comment, source, contact) VALUES (%s, %s, %s, %s);",
                       (update, comment, source, contact))
        source += 1

      except PgSQL.OperationalError:
        print "failure on comment=%s update=%s" % (comment, update)
        return

    else:
      print "updated comment=%s where update=%s" % (comment, update)
      return

  sys.path.append("../../backend")
  import osmose_config

  for (country, country_config) in osmose_config.config.items():
    for k, v in country_config.analyser.items():
      if v != "xxx":
        update_pass("%s-%s" % (k, country), v)

  dbconn.commit()
  dbconn.close()
