#! /usr/bin/env python
#-*- coding: utf-8 -*-

import os, re, Cookie

################################################################################

allowed_languages = ["en", "fr", "nl", "de", "it"]
pg_user           = "osmose"
pg_pass           = "clostAdtoi"
pg_base           = "osmose"
website           = "osmose.openstreetmap.fr"

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

def get_categories(lang):
    result = []
    conn = get_dbconn()
    curs1 = conn.cursor()
    curs2 = conn.cursor()
    curs1.execute("SELECT categ, menu FROM dynpoi_categ ORDER BY categ")
    for res1 in curs1.fetchall():
        res = {"categ":res1[0], "menu": "no translation", "item":[]}
        for l in lang:
            if l in res1[1]:
                res["menu"] = res1[1][l]
                break
        curs2.execute("SELECT item, menu, marker_color, marker_flag, levels FROM dynpoi_item WHERE categ = %d ORDER BY item"%res1[0])
        for res2 in curs2.fetchall():
            res["item"].append({"item":res2[0], "menu":"no translation", "marker_color":res2[2], "marker_flag":res2[3], "levels": res2["levels"]})
            for l in lang:
                if res2[1] and l in res2[1]:
                    res["item"][-1]["menu"] = res2[1][l]
                    break

        result.append(res)
    return result

def show(s):
    print s.encode("utf8")

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
