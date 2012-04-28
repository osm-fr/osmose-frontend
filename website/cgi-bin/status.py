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

import sys, os, cgi
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import osmose_common

form      = cgi.FieldStorage()

###########################################################################

print "Content-Type: text/html; charset=utf-8"
print

error_id = int(form.getvalue("e", -1))
status = form.getvalue("s", None)
if status not in ["done","false"]:
    sys.exit(1)
if error_id < 0:
    sys.exit(1)

if osmose_common.remove_bug(error_id, "done") == 0:
  print "OK"
else:
  print "FAIL"
