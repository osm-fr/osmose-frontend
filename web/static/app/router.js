import Vue from 'vue'
import VueRouter from 'vue-router'

import IssueIndex from './pages/issue/index.vue'
import FalsepositiveIndex from './pages/false-positive/index.vue'
import IssuesIndex from './pages/issues/index.vue'
import IssuesMatrix from './pages/issues/matrix.vue'
import ByUserIndex from './pages/byuser/index.vue'
import ByUserList from './pages/byuser/byuser.vue'

Vue.use(VueRouter)

export const router = new VueRouter({
    mode: 'history',
    routes: [
        { path: '/:lang/error/:uuid', component: IssueIndex },
        { path: '/:lang/errors/', component: IssuesIndex },
        { path: '/:lang/errors/done', component: IssuesIndex },
        { path: '/:lang/errors/false-positive', component: IssuesIndex },
        { path: '/:lang/false-positive/:uuid', component: FalsepositiveIndex },
        { path: '/:lang/issues/matrix', component: IssuesMatrix },
        { path: '/:lang/byuser', component: ByUserIndex },
        { path: '/:lang/byuser/:user', component: ByUserList },
    ],
});
