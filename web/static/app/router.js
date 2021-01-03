import Vue from 'vue'
import VueRouter from 'vue-router'

import IssueIndex from './pages/issue/index.vue'
import FalsepositiveIndex from './pages/false-positive/index.vue'

Vue.use(VueRouter)

export const router = new VueRouter({
    mode: 'history',
    routes: [
        { path: '/:lang/error/:uuid', component: IssueIndex },
        { path: '/:lang/false-positive/:uuid', component: FalsepositiveIndex },
    ],
});
