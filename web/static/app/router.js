import Vue from 'vue'
import VueRouter from 'vue-router'

import Index from './pages/index.vue'
import Contact from './pages/contact.vue'
import Copyright from './pages/copyright.vue'
import Translation from './pages/translation.vue'

import IssueIndex from './pages/issue/index.vue'
import FalsepositiveIndex from './pages/false-positive/index.vue'
import IssuesIndex from './pages/issues/index.vue'
import IssuesMatrix from './pages/issues/matrix.vue'
import ByUserIndex from './pages/byuser/index.vue'
import ByUserList from './pages/byuser/byuser.vue'

import ControlUpdate from './pages/control/update.vue'
import ControlUpdates from './pages/control/updates.vue'
import ControlUpdateMatrix from './pages/control/update_matrix.vue'
import ControlUpdateSummary from './pages/control/update_summary.vue'
import ControlUpdateSummaryByAanalyser from './pages/control/update_summary_by_analyser.vue'
// TODO
// ControlUpdateSummaryByAanalyser =
//     import ( /* webpackChunkName: "control" */ './pages/control/update_summary_by_analyser.vue')


Vue.use(VueRouter)

export const router = new VueRouter({
    mode: 'history',
    routes: [
        { path: '/:lang/', component: Index },
        { path: '/:lang/contact', component: Contact },
        { path: '/:lang/copyright', component: Copyright },
        { path: '/:lang/translation', component: Translation },

        { path: '/:lang/error/:uuid', component: IssueIndex },
        { path: '/:lang/errors/', component: IssuesIndex },
        { path: '/:lang/errors/done', component: IssuesIndex },
        { path: '/:lang/errors/false-positive', component: IssuesIndex },
        { path: '/:lang/false-positive/:uuid', component: FalsepositiveIndex },
        { path: '/:lang/issues/matrix', component: IssuesMatrix },
        { path: '/:lang/byuser', component: ByUserIndex },
        { path: '/:lang/byuser/:user', component: ByUserList },

        { path: '/:lang/control/update', component: ControlUpdates },
        { path: '/:lang/control/update/:source_id', component: ControlUpdate },
        { path: '/:lang/control/update_matrix', component: ControlUpdateMatrix },
        { path: '/:lang/control/update_summary', component: ControlUpdateSummary },
        { path: '/:lang/control/update_summary_by_analyser', component: ControlUpdateSummaryByAanalyser },
    ],
});
