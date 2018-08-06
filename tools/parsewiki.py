#-*- coding: utf-8 -*-

###########################################################################
##                                                                       ##
## Copyrights Frédéric Rodrigo 2014-2015                                 ##
##                                                                       ##
## This program is free software: you can redistribute it and/or modify  ##
## it under the terms of the GNU General Public License as published by  ##
## the Free Software Foundation, either version 3 of the License, or     ##
## (at your option) any later version.                                   ##
##                                                                       ##
## This program is distributed in the hope that it will be useful,       ##
## but WITHOUT ANY WARRANTY; without even the implied warranty of        ##
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         ##
## GNU General Public License for more details.                          ##
##                                                                       ##
## You should have received a copy of the GNU General Public License     ##
## along with this program.  If not, see <http://www.gnu.org/licenses/>. ##
##                                                                       ##
###########################################################################

import re
import utils


def listitem(lang):
    conn = utils.get_dbconn()
    curs = conn.cursor()

    items = {}

    curs.execute("SELECT categ, COALESCE(menu->'%s', menu->'en') AS menu FROM dynpoi_categ;" % lang)
    for res in curs.fetchall():
        items[res['categ']] = dict(res)
        items[res['categ']]['item'] = {}

    curs.execute("SELECT item, categ, COALESCE(menu->'%s', menu->'en') AS menu FROM dynpoi_item;" % lang)
    for res in curs.fetchall():
        items[res['categ']]['item'][res['item']] = dict(res)
        items[res['categ']]['item'][res['item']]['class'] = {}

    curs.execute("SELECT class, dynpoi_class.item, dynpoi_item.categ, COALESCE(Max(title->'%s'), Max(title->'en')) AS title FROM dynpoi_class JOIN dynpoi_item ON dynpoi_item.item=dynpoi_class.item GROUP BY class, dynpoi_class.item, dynpoi_item.categ" % lang)
    for res in curs.fetchall():
        if items[res['categ']]['item'].get(res['item']):
            items[res['categ']]['item'][res['item']]['class'][res['class']] = res['title']

    return items

header = {
    'de': 'Artikel || Hilfe || Beispiel',
    'en': 'Item || Help || Example',
    'fr': 'Item || Aide || Exemple',
    'it': 'Articolo || Aiuto || Esempio',
    'nl': 'Item || Help || Voorbeeld',
    'uk': 'Проблема || Допомога || Приклад',
    'ja': '項目 || 説明 || 例',
}

classs = {
    'de': 'Class',
    'en': 'Class',
    'fr': 'Classe',
    'it': 'Class',
    'nl': 'Class',
    'uk': 'Class',
    'ja': 'Class',
}

def parsewiki(lang):
    ref = listitem(lang)

    LANG = lang.upper() + ":" if lang != "en" else ""

    #data = urlread("http://wiki.openstreetmap.org/w/index.php?title=FR:Osmose/issues&action=raw", 1)
    data = open("index.php?title=" + LANG + "Osmose%2Fissues&action=raw").read()
    data = data.split("\n")
    in_error = False
    errors = {0: []}
    accu = {}
    key = None
    categ = 0
    for line in data:
        line = line.strip()
        if line.startswith('{{Osmose Error'):
            in_error = True

        if in_error and line.startswith('}}'):
            errors[categ][int(accu['item']['text'])] = accu
            in_error = False
            accu = {}
            key = None
        elif in_error:
            if line.startswith('|'):
                key, line = line[1:].strip().split('=', 1)
                accu[key] = {'text': '', 'class': {}}
                line = line.strip()
            if line.startswith("* " + classs[lang] + " "):
                dclass = line[len("* " + classs[lang] + " "):].split('" : ', 1)
                nclass = int(dclass[0].split(' ')[0].strip())
                accu[key]['class'][nclass] = dclass[1].strip() if len(dclass)> 1 else ""
            elif key:
                accu[key]['text'] += line + "\n"
        else:
            if line.startswith('='):
                categ += 10
                errors[categ] = {}
            if categ == 0:
                errors[categ].append(line)

    for line in errors[0]:
        print line

    for categ in sorted(ref.keys()):
        print ("=%s=" % ref[categ]['menu'].encode('utf-8'))
        print ("{| class=\"wikitable sortable\" style=\"width:100%\"\n|-\n! " + header[lang] + "\n|-\n")
        for item in sorted(ref[categ]['item']):
            print "{{Osmose Error|format={{{format|para}}}"
            if not errors[categ].get(item):
                errors[categ][item] = {'item': {'text': item, 'class': {}}}
            if not errors[categ][item].get('label'):
                errors[categ][item]['label'] = {'text': None, 'class': {}}
            errors[categ][item]['label']['text'] = ref[categ]['item'][item]['menu'].encode('utf-8') if ref[categ]['item'][item]['menu'] else ""
            val = errors[categ][item]
            for k in ('item', 'label', 'only_for', 'detail', 'fix', 'trap', 'image'):
                if k != 'image' and not val.has_key(k):
                    val[k] = {'text': '', 'class': {}}
                if val.has_key(k):
                    print ("| %s=%s" % (k, val[k]['text'])).strip()
                    if len(ref[categ]['item'][item]['class'].keys()) > 1:
                        for c in sorted(ref[categ]['item'][item]['class'].keys()):
                            if k in ('detail', 'fix'):
                                print ("* %s %s \"%s\" : %s" % (classs[lang], c, (ref[categ]['item'][item]['class'][c] or '').encode('utf-8').replace('|', '&#124;'), val[k]['class'].get(c, '')))
            print "}}\n"
        print "|}\n"


if __name__ == "__main__":

    parsewiki('ja')
