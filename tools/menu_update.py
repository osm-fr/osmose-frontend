#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import codecs
import os

import polib

from modules_legacy import utils


class OsmoseTranslation:
    def __init__(self):
        self.languages = []
        self.trans = {}
        for fn in os.listdir("../web/po/"):
            if not fn.endswith(".po"):
                continue

            lang = fn[:-3]
            self.languages.append(lang)
            po = polib.pofile("../web/po/" + lang + ".po")
            self.trans[lang] = {}
            for entry in po:
                if entry.msgstr != "":
                    self.trans[lang][entry.msgid] = entry.msgstr

    def translate(self, str):
        out = {}
        out["en"] = str  # english version
        for lang in self.languages:
            if str in self.trans[lang] and self.trans[lang][str] != "":
                out[lang] = self.trans[lang][str]
        return out


async def main():
    t = OsmoseTranslation()

    dbconn = utils.get_dbconn()
    dbcurs = dbconn.cursor()

    types = {"categories": "id", "items": "item"}

    for typ, id in types.items():
        sql = (
            "update "
            + typ
            + " set menu = coalesce(menu, json_build_object(%s,'')::jsonb) || json_build_object(%s, %s)::jsonb where "
            + id
            + " = %s;"
        )

        for line in codecs.open("database/" + typ + "_menu.txt", "r", "utf-8"):
            (item, s) = line.split("|")
            item_i = int(item)
            s = s.strip()[3:-2]
            translations = t.translate(s)
            for (l, s) in translations.items():
                dbcurs.execute(sql, (l, l, s, item_i))

    dbconn.commit()


if __name__ == "__main__":
    asyncio.run(main())
