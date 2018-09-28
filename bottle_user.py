'''
'''

__author__ = "Frederic Rodrigo"
__version__ = '0.1'
__license__ = 'MIT'

### CUT HERE (see setup.py)

from bottle import request, response
import inspect


class UserPlugin(object):
    '''
    '''

    name = 'user'
    api  = 2

    def __init__(self, keyword='user'):
        self.keyword = keyword

    def apply(self, callback, route):
        conf = route.config.get('user') or {}
        keyword = conf.get('keyword', self.keyword)

        # Test if the original callback accepts a 'user' keyword.
        # Ignore it if it does not need a database handle.
        args = inspect.getargspec(route.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            if request.session.has_key('user'):
                if request.session['user']:
                    user = request.session['user']['osm']['user']['@display_name']
                else:
                    user = False
            else:
                user = None

            # Add the user as a keyword argument.
            kwargs[keyword] = user

            return callback(*args, **kwargs)

        return wrapper

Plugin = UserPlugin
