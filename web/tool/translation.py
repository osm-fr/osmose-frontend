#! /usr/bin/env python
#-*- coding: utf-8 -*-


class translator:

    _direction_rtl = ['fa', 'ar', 'he', 'ff', 'yi', 'ur', 'rgh', 'man', 'syc', 'mid', 'dv']

    def __init__(self, language):
        self.languages = language
        self.direction = 'rtl' if self.languages[0].split('_')[0] in self._direction_rtl else 'ltr'

    def select(self, res, no_translation = ""):
        # res is a dictionnary of possible translations, given by a SQL query
        if not res:
            return ""
        for l in self.languages:
            if l in res:
                return res[l]
        return no_translation
