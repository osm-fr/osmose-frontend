#! /usr/bin/env python
#-*- coding: utf-8 -*-

import os, re, Cookie
import datetime, urllib2
from collections import OrderedDict
import pwd
import OsmSax

################################################################################

languages_name = OrderedDict()
languages_name["en"] = u"English"

# language names from http://en.wikipedia.org/wiki/List_of_ISO_639-1_codes
languages_name["ca"] = u"Català"
languages_name["cs"] = u"Čeština"
languages_name["da"] = u"Dansk"
languages_name["de"] = u"Deutsch"
languages_name["el"] = u"Ελληνικά"
languages_name["es"] = u"Español"
languages_name["eu"] = u"Euskara"
languages_name["fa"] = u"فارسی"
languages_name["fi"] = u"Suomi"
languages_name["fr"] = u"Français"
languages_name["gl"] = u"Galego"
languages_name["hu"] = u"Magyar"
languages_name["it"] = u"Italiano"
languages_name["ja"] = u"日本語"
languages_name["lt"] = u"Lithuanian"
languages_name["nb"] = u"Norsk bokmål"
languages_name["nl"] = u"Nederlands"
languages_name["pl"] = u"Polski"
languages_name["pt"] = u"Português"
languages_name["pt_BR"] = u"Português (Brasil)"
languages_name["ro"] = u"Română"
languages_name["ru"] = u"Русский"
languages_name["uk"] = u"Українська"
languages_name["vi"] = u"Tiếng Việt"
languages_name["zh_CN"] = u"中文 (简体)"
languages_name["zh_TW"] = u"中文 (繁體)"

allowed_languages = list(languages_name)
pg_host           = os.environ.get('DB_HOST', '') # Use socket by default
pg_port           = "5432"
pg_user           = "osmose"
pg_pass           = "-osmose-"
pg_base           = "osmose_frontend"
db_string         = "host='%s' port='%s' dbname='%s' user='%s' password='%s'" % (pg_host, pg_port, pg_base, pg_user, pg_pass)

website           = os.environ.get('URL_FRONTEND') or "osmose.openstreetmap.fr"

main_project      = "OpenStreetMap"
main_website      = "https://www.openstreetmap.org/"
remote_url        = "https://www.openstreetmap.org/"
remote_url_read   = "https://www.openstreetmap.org/"
remote_url_write  = "https://www.openstreetmap.org/"

#main_project      = "OpenGeoFiction"
#main_website      = "http://opengeofiction.net/"
#remote_url        = "http://opengeofiction.net/"
#remote_url_read   = "http://opengeofiction.net/"
#remote_url_write  = "http://opengeofiction.net/"
#main_website      = "http://opengeofiction.net/"

username          = pwd.getpwuid(os.getuid())[0]
dir_results       = "/data/work/%s/results" % (username)

################################################################################

def get_dbconn():
    import psycopg2.extras
#    return psycopg2.connect(host="localhost", database = pg_base, user = pg_user, password = pg_pass)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
    psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)
    conn = psycopg2.extras.DictConnection(db_string)
    psycopg2.extras.register_default_jsonb(conn)
    return conn

def pg_escape(text):
    if text is None:
        return None
    if type(text) == int:
        return str(text)
    return text.replace(u"'", u"''").replace(u'\\',u'\\\\')

def get_sources():
    conn = get_dbconn()
    curs = conn.cursor()
    curs.execute("SELECT id, password, country, analyser FROM source JOIN source_password ON source.id = source_id;")
    config = {}
    for res in curs.fetchall():
        src = {}
        src["id"]         = str(res["id"])
        src["password"]   = set([res["password"]])
        src["country"]    = res["country"]
        src["analyser"]   = res["analyser"]
        src["comment"]    = res["analyser"] + "-" + res["country"]
        if (src["id"] in config and
            config[src["id"]]["country"] == src["country"] and
            config[src["id"]]["analyser"] == src["analyser"]):
            config[src["id"]]["password"].update(src["password"])
        else:
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

    _direction_rtl = ['fa', 'ar', 'he', 'ff', 'yi', 'ur', 'rgh', 'man', 'syc', 'mid', 'dv']

    def __init__(self, language):
        self.languages = language
        self.direction = 'rtl' if self.languages[0].split('_')[0] in self._direction_rtl else 'ltr'

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
    try:
        elem_io = urllib2.urlopen(elem_url)
        osm_read = OsmSax.OsmSaxReader(elem_io)
        return osm_read
    except:
        pass

def fetch_osm_elem(type, id):
    osmdw = OsmSax.OsmDictWriter()
    osm_read = fetch_osm_data(type, id, full=False)
    if osm_read:
        osm_read.CopyTo(osmdw)
        elem = osmdw.data[type]
        if len(elem) > 0:
            return elem[0]
