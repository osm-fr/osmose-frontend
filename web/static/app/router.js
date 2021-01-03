import Vue from 'vue'
import VueRouter from 'vue-router'

import IssueIndex from './issue/index.vue'

Vue.use(VueRouter)

export const router = new VueRouter({
    mode: 'history',
    routes: [
        { path: '/:lang/error/:uuid', component: IssueIndex },
    ],
});
