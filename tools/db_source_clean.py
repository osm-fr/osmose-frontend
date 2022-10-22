#! /usr/bin/env python
#-*- coding: utf-8 -*-

from modules_legacy import utils

if __name__ == "__main__":

    sources = [int(x) for x in utils.get_sources().keys()]
    dbconn  = utils.get_dbconn()
    dbcurs  = dbconn.cursor()

    tables  = ["markers_counts", "markers", "markers_status", "updates"]
    for t in tables:
        dbcurs.execute("SELECT source_id FROM %s GROUP BY source_id;"%t)
        for res in dbcurs.fetchall():
            if res[0] not in sources:
                print("DELETE FROM %s WHERE source_id = %d;"%(t, res[0]))
