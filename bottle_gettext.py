'''
'''

__author__ = "Frederic Rodrigo"
__version__ = '0.1'
__license__ = 'MIT'

### CUT HERE (see setup.py)

from bottle import request
import gettext, inspect


class GettextPlugin(object):
    '''
    '''

    name = 'gettext'
    api  = 2

    def __init__(self, domain, localedir, allowed_languages, keyword='lang'):
        self.domain = domain
        self.localedir = localedir
        self.allowed_languages = allowed_languages
        self.keyword = keyword
        self.cache = {}

    def get_language(self):
        lang = [None]

        if len(request.script_name) > 3:
            lang = [request.script_name[-3:-1]]
            if lang[0] not in self.allowed_languages:
                lang = [None]

        if not lang[0]:
            lang = [request.get_cookie('lang')]
            if lang[0] not in self.allowed_languages:
                lang = [None]

        if not lang[0] and request.get_header('Accept-Language'):
            lang = request.get_header('Accept-Language')
            lang = lang.split(',')
            lang = [x.split(";")[0] for x in lang]
            lang = [x.split("-")[0] for x in lang]
            lang = [x for x in lang if x in self.allowed_languages]

        if len(lang) > 0 and lang[0]:
            lang.append(self.allowed_languages[0])
            res = []
            for l in lang:
                if not l in res:
                    res.append(l)
            return res
        else:
            return self.allowed_languages

    def apply(self, callback, route):
        conf = route.config.get('pgsql') or {}
        keyword = conf.get('keyword', self.keyword)

        def wrapper(*args, **kwargs):
            language = self.get_language()

            # Setup Gettext
            k = ','.join(language)
            if self.cache.has_key(k):
                gt = self.cache[k]
            else:
                gt = gettext.translation(self.domain, localedir=self.localedir, languages=language)
                self.cache[k] = gt
            gt.install(unicode=1)

            # Add the language as a keyword argument.
            if keyword in inspect.getargspec(route.callback)[0]:
                kwargs[keyword] = language

            return callback(*args, **kwargs)

        return wrapper

Plugin = GettextPlugin
