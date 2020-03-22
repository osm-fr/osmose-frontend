#!/usr/bin/env python
#-*- coding: utf-8 -*-

import codecs
import os
import polib
from . import utils

class OsmoseTranslation:

    def __init__(self):
        self.languages = []
        self.trans = {}
        for fn in os.listdir("../web/po/"):
            if not fn.endswith(".po"):
                continue

            l = fn[:-3]
            self.languages.append(l)
            po = polib.pofile("../web/po/" + l + ".po")
            self.trans[l] = {}
            for entry in po:
                if entry.msgstr != "":
                    self.trans[l][entry.msgid] = entry.msgstr

    def translate(self, str, args=()):
        out = {}
        out["en"] = str % args   # english version
        for l in self.languages:
            if str in self.trans[l] and self.trans[l][str] != "":
                out[l] = self.trans[l][str] % args
        return out

if __name__ == "__main__":

  t = OsmoseTranslation()

  dbconn = utils.get_dbconn()
  dbcurs = dbconn.cursor()

  types = ("categ", "item")

  for typ in types:
    sql = "update dynpoi_" + typ + " set menu = coalesce(menu, json_build_object(%s,'')::jsonb) || json_build_object(%s, %s)::jsonb where " + typ + " = %s;"

    for line in codecs.open("database/" + typ + "_menu.txt", "r", "utf-8"):
      (item, s) = line.split("|")
      item = int(item)
      s = s.strip()[3:-2]
      translations = t.translate(s)
      for (l, s) in translations.items():
        dbcurs.execute(sql, (l, l, s, item))

  dbconn.commit()
