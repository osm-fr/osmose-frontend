import Vue from 'vue'
import VueI18n from 'vue-i18n'

import messages from '../po/en.po'

Vue.use(VueI18n)

export const i18n = new VueI18n({
  locale: 'en', // set locale
  fallbackLocale: 'en',
  formatFallbackMessages: true,
  silentTranslationWarn: true,
  messages, // set locale messages
})

const loadedLanguages = ['en'] // our default language that is preloaded

function setI18nLanguage(lang: string): string {
  i18n.locale = lang
  document.querySelector('html').setAttribute('lang', lang)
  return lang
}

export function loadLanguageAsync(lang: string): Promise<String | void> {
  if (!lang) {
    return Promise.resolve()
  }

  // If the same language
  if (i18n.locale === lang) {
    return Promise.resolve(setI18nLanguage(lang))
  }

  // If the language was already loaded
  if (loadedLanguages.includes(lang)) {
    return Promise.resolve(setI18nLanguage(lang))
  }

  // If the language hasn't been loaded yet
  return import(
    /* webpackChunkName: "lang-[request]" */ `../po/${lang}.po`
  ).then((messages) => {
    i18n.setLocaleMessage(lang, messages.default)
    loadedLanguages.push(lang)
    return setI18nLanguage(lang)
  })
}
