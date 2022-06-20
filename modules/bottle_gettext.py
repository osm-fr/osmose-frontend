"""
"""

__author__ = "Frederic Rodrigo"
__version__ = "0.1"
__license__ = "MIT"

### CUT HERE (see setup.py)

import gettext
import inspect

from bottle import request, response


class GettextPlugin(object):
    """"""

    name = "gettext"
    api = 2

    def __init__(self, domain, localedir, allowed_languages, keyword="lang"):
        self.domain = domain
        self.localedir = localedir
        self.allowed_languages = allowed_languages
        self.keyword = keyword
        self.cache = {}

    def get_language(self):
        lang = [None]

        if len(request.script_name) > 3:
            tmp_lang = request.script_name[1:3]
            if tmp_lang in self.allowed_languages:
                return ([tmp_lang, self.allowed_languages[0]], False)

            # Handle longer languages like zh_TW
            if len(request.script_name) > 6 and request.script_name[-4] == "_":
                tmp_lang = request.script_name[1:6]
                if tmp_lang in self.allowed_languages:
                    return ([tmp_lang, self.allowed_languages[0]], False)

            lang = [None]

        if not lang[0] and request.get_header("Accept-Language"):
            lang = request.get_header("Accept-Language")
            lang = lang.split(",")
            lang = [x.split(";")[0] for x in lang]
            lang = [x.split("-")[0] for x in lang]
            lang = [x for x in lang if x in self.allowed_languages]

        if len(lang) > 0 and lang[0]:
            lang.append(self.allowed_languages[0])
            res = []
            for l in lang:
                if not l in res:
                    res.append(l)
            return (res, True)
        else:
            return (self.allowed_languages, True)

    def apply(self, callback, route):
        conf = route.config.get("gettext") or {}
        keyword = conf.get("keyword", self.keyword)

        # Test if the original callback accepts a 'lang' keyword.
        # Ignore it if it does not need a gettext handle.
        args = inspect.getfullargspec(route.callback)[0]
        if keyword not in args:
            return callback

        def wrapper(*args, **kwargs):
            (language, redirect) = self.get_language()

            if redirect:
                from bottle import redirect

                from . import utils

                url = request.urlparts
                new_url = []
                new_url.append("/" + language[0])
                new_url.append(request.fullpath)
                if url.query:
                    new_url.append("?")
                    new_url.append(url.query)
                redirect("".join(new_url))
                return

            # Setup Gettext
            k = ",".join(language)
            if k in self.cache:
                gt = self.cache[k]
            else:
                gt = gettext.translation(
                    self.domain, localedir=self.localedir, languages=language
                )
                self.cache[k] = gt
            gt.install()

            # Add the language as a keyword argument.
            kwargs[keyword] = language

            return callback(*args, **kwargs)

        return wrapper


Plugin = GettextPlugin
