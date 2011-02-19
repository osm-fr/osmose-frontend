#!/usr/bin/env python

import os, sys
root_folder = os.environ["OSMOSE_ROOT"]
sys.path.append(root_folder)
from tools import utils

print "Content-Type: text/plain; charset=utf-8"
print
print os.environ["HTTP_ACCEPT_LANGUAGE"]
print utils.get_language()
