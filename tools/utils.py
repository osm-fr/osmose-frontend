#! /usr/bin/env python
#-*- coding: utf-8 -*-

import os, re, Cookie
import datetime, urllib2
import OsmSax

################################################################################

allowed_languages = ["en", "fr", "de", "es", "it", "nl", "sw"]
pg_user           = "osmose"
pg_pass           = "clostAdtoi"
pg_base           = "osmose_frontend"
website           = "osmose.openstreetmap.fr"

remote_url        = "http://api.openstreetmap.org/"
remote_url_read   = "http://api.openstreetmap.fr/"
remote_url_write  = "http://api.openstreetmap.org/"

################################################################################

def get_dbconn():
    import psycopg2.extras
#    return psycopg2.connect(host="localhost", database = pg_base, user = pg_user, password = pg_pass)
    db_string = "host='localhost' dbname='%s' user='%s' password='%s'" % (pg_base, pg_user, pg_pass)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
    conn = psycopg2.extras.DictConnection(db_string)
    psycopg2.extras.register_hstore(conn, unicode=True)
    return conn

def pg_escape(text):
    if type(text) == int:
        return str(text)
    return text.replace(u"'", u"''").replace(u'\\',u'\\\\')

def get_sources():
    conn = get_dbconn()
    curs = conn.cursor()
    curs.execute("SELECT source, update, comment, contact FROM dynpoi_source;")
    config = {}
    for res in curs.fetchall():
        src = {}
        src["id"]         = str(res["source"])
        src["updatecode"] = res["update"]
        src["comment"]    = res["comment"]
        src["contact"]    = res["contact"]
        config[src["id"]] = src
    return config

def show(s):
    print s.encode("utf8")

def str_to_datetime(s):
    patterns = [
                "%Y-%m-%d",
                "%Y-%m",
                "%Y"
               ]
    for p in patterns:
        try:
            return datetime.datetime.strptime(s, p)
        except ValueError:
            pass

    raise ValueError

###########################################################################
## translation

class translator:

    def __init__(self, language):
        self.languages = language

    def select(self, res, no_translation = ""):
        # res is a dictionnary of possible translations, given by a SQL query
        if not res:
            return ""
        for l in self.languages:
            if l in res:
                return res[l]
        return no_translation

###########################################################################
## API

def fetch_osm_data(type, id, full=True):
    elem_url = os.path.join(remote_url_read + 'api/0.6/', type, str(id))
    if type == "way" and full:
        elem_url = os.path.join(elem_url, "full")
    elem_io = urllib2.urlopen(elem_url)
    osm_read = OsmSax.OsmSaxReader(elem_io)

    return osm_read

def fetch_osm_elem(type, id):
    osmdw = OsmSax.OsmDictWriter()
    osm_read = fetch_osm_data(type, id, full=False)
    osm_read.CopyTo(osmdw)
    elem = osmdw.data[type]
    if len(elem) > 0:
        return elem[0]
