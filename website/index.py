#! /usr/bin/env python
#-*- coding: utf-8 -*-
###########################################################################
##                                                                       ##
## Copyrights Etienne Chové <chove@crans.org> 2009                       ##
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

###########################################################################
## database connection

import sys, os, time, cgi
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

PgConn    = utils.get_dbconn()
PgCursor  = PgConn.cursor()
translate = utils.translator()

###########################################################################
## page headers

utils.print_header(translate)


print "<h1>Osmose</h1>"

print "<ul>"
print "<li> <a href='map'>Carte des erreurs</a>"
print "<li> <a href='http://wiki.openstreetmap.org/wiki/FR:Osmose'>Aide sur le wiki d'OSM</a>"
print "</ul>"

print "<h2>Information sur la base de donnée</h2>"
print "<ul>"
print "<li> <a href='utils/false-positive.py'>Liste des faux positifs</a>"
print "<li> <a href='utils/last-update.py'>Dernières mises à jour des analyses</a>"

print "</ul>"


###########################################################################
## page end

utils.print_tail()
