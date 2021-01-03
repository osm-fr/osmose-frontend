import Vue from 'vue'
import { router } from './router.js'
import { i18n, loadLanguageAsync } from './i18n.js'
import SortedTablePlugin from "vue-sorted-table"

import App from './app.vue'

Vue.use(SortedTablePlugin);

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
