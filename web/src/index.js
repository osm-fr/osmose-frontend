import Vue from 'vue'
import { router } from './router.js'
import { i18n, loadLanguageAsync } from './i18n.js'
import SortedTablePlugin from "vue-sorted-table"
import numeral from 'numeral'
import numFormat from 'vue-filter-number-format'
import vueTopprogress from 'vue-top-progress'

import App from './app.vue'
import Translate from "./components/translate.vue";
import TranslateSlot from "./components/translate-slot.vue";

Vue.use(vueTopprogress)
Vue.use(SortedTablePlugin);
Vue.filter('numFormat', numFormat(numeral));
Vue.component('translate', Translate)
Vue.component('translate-slot', TranslateSlot)

document.addEventListener("DOMContentLoaded", (event) => {
    router.beforeEach((to, from, next) => {
        const lang = to.params.lang
        loadLanguageAsync(lang).then(() => next())
    });

    new Vue({
        el: '#app',
        router,
        i18n,
        render: (h) => h(App),
    });
});
