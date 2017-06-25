'''
'''

__author__ = "Frederic Rodrigo"
__version__ = '0.1'
__license__ = 'MIT'

### CUT HERE (see setup.py)

from bottle import request, response


class CorsPlugin(object):
    '''
    '''

    name = 'cors'
    api  = 2

    def __init__(self, allow_origin='*', preflight_methods=['GET', 'POST', 'PUT', 'DELETE']):
        self.allow_origin = allow_origin
        self.preflight_methods = ', '.join(preflight_methods)

    def apply(self, callback, route):
        def wrapper(*args, **kwargs):
            # set CORS headers
            response.headers['Access-Control-Allow-Origin'] = self.allow_origin
            response.headers['Access-Control-Allow-Methods'] = self.preflight_methods

            if request.method != 'OPTIONS':
                # actual request; reply with the actual response
                return callback(*args, **kwargs)

        return wrapper

Plugin = CorsPlugin
