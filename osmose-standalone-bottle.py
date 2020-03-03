#!/usr/bin/env python
# -*- coding: utf-8 -*-

#
# Copyright 2012 Frederic Rodrigo
#
#

import bottle

import osmose

bottle.run(app=osmose.app_middleware, host='0.0.0.0', port=20009, reloader=True, debug=True)
