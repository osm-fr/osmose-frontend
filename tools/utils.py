#! /usr/bin/env python
#-*- coding: utf8 -*-

import os, atexit
from xml.sax import make_parser, handler

################################################################################

root_folder       = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
allowed_languages = ["en", "fr"]
translation_file  = os.path.join(root_folder, "config/translate.txt")
config_file       = os.path.join(root_folder, "config/config.xml")
pg_user           = "osmose"
pg_base           = "osmose"

################################################################################

def get_dbconn():
    from pyPgSQL import PgSQL
    return PgSQL.connect(database = pg_base, user = pg_user)

def pg_escape(text):
    if type(text) == int:
        return str(text)
    return text.replace(u"'", u"''").replace(u'\\',u'\\\\')

def get_language():
    if "HTTP_ACCEPT_LANGUAGE" in os.environ:
        lg = os.environ["HTTP_ACCEPT_LANGUAGE"]
        lg = lg.split(",")
        lg = [x.split(";")[0] for x in lg]
        lg = [x.split("-")[0] for x in lg]
        lg = [x for x in lg if x in allowed_languages]
        if lg:
            return lg[0]
    return allowed_languages[0]

def get_sources(lang = get_language()):
    if lang not in allowed_languages:
        lang = allowed_languages[0]
    conn = get_dbconn()
    curs = conn.cursor()
    curs.execute("SELECT source, update, comment, contact FROM dynpoi_source;")
    config = {}
    for res in curs.fetchall():
        src = {}
        src["id"]         = str(res["source"])
        src["updatecode"] = str(res["update"])
        src["comment"]    = str(res["comment"])
        src["contact"]    = str(res["contact"])        
        config[src["id"]] = src
    return config

def get_categories(lang = get_language()):
    if lang not in allowed_languages:
        lang = allowed_languages[0]
    result = []
    conn = get_dbconn()
    curs1 = conn.cursor()
    curs2 = conn.cursor()
    curs1.execute("SELECT categ, menu_%s, menu_%s FROM dynpoi_categ ORDER BY categ"%(lang, allowed_languages[0]))
    for res1 in curs1.fetchall():
        res = {"categ":res1[0], "menu": (res1[1] or res1[2] or "no translation").decode("utf8"), "item":[]}
        curs2.execute("SELECT item, menu_%s, menu_%s, marker_color, marker_flag FROM dynpoi_item WHERE categ = %d ORDER BY item"%(lang, allowed_languages[0], res1[0]))
        for res2 in curs2.fetchall():
            res["item"].append({"item":res2[0], "menu":(res2[1] or res2[2] or "no translation").decode("utf8"), "marker_color":res2[3], "marker_flag":res2[4]})
        result.append(res)
    return result

class translator:
    
    def __init__(self, language = get_language(), default_language = allowed_languages[0], translation = translation_file):

        self.client_language = language
        self.default_language = default_language
        
        self._data = {}
        for l in open(translation).readlines():
            l = l.strip()
            if l.startswith("#"):
                continue
            if not l:
                continue
            l = l.split(" ", 1)
            self._data[l[0]] = l[1].strip().decode("utf8")
                
    def get(self, item, args = None):
        
        if "%s.%s" % (self.client_language, item) in self._data:
            item = self._data["%s.%s" % (self.client_language, item)]
        elif "%s.%s" % (self.default_language, item) in self._data:
            item = self._data["%s.%s" % (self.default_language, item)]
        else:
            item = u"no translation"
            
        if args:
            for i in range(len(args)):
                item = item.replace(u"$%d"%i, args[i])
        
        return item
