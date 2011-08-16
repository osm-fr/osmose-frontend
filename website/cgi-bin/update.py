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
from tools import utils
from tools import update

if __name__ == "__main__":
    print "Content-Type: text/plain; charset=utf-8"
    print

    form = cgi.FieldStorage()

    if not "code" in form or not "url" in form:
        print "FAIL"
        sys.exit(1)

    code = form["code"].value
    url  = form["url"].value
    #print code
    #print url
    
    sources = utils.get_sources()
    for s in sources:
        if sources[s].get("updatecode", 0) <> code:
            continue
        #sources['url'] = url
        try:
            update.update(sources[s], url)
        except:
            import traceback
            from cStringIO import StringIO
            import smtplib
            s = StringIO()
            sys.stderr = s
            traceback.print_exc()
            sys.stderr = sys.__stderr__
            traceback = s.getvalue()
            print traceback.rstrip()
            sys.exit(1)
        #print sources[s]
        print "OK"
        sys.exit(0)

    print "AUTH FAIL"
    sys.exit(1)
