import Vue from 'vue'
import VueRouter from 'vue-router'

import NotFound from './components/404.vue'

const Index = () => import(/* webpackChunkName: "index" */ './pages/index.vue')
const Contact = () =>
  import(/* webpackChunkName: "contact" */ './pages/contact.vue')
const Copyright = () =>
  import(/* webpackChunkName: "copyright" */ './pages/copyright.vue')
const Translation = () =>
  import(/* webpackChunkName: "translation" */ './pages/translation.vue')

const Map = () => import(/* webpackChunkName: "map" */ './pages/map/index.vue')

const IssueIndex = () =>
  import(/* webpackChunkName: "issue" */ './pages/issue/index.vue')
const IssuesIndex = () =>
  import(/* webpackChunkName: "issues" */ './pages/issues/index.vue')
const ByUserIndex = () =>
  import(/* webpackChunkName: "issues" */ './pages/byuser/index.vue')
const ByUserList = () =>
  import(/* webpackChunkName: "issues" */ './pages/byuser/byuser.vue')
const IssuesMatrix = () =>
  import(/* webpackChunkName: "issues_matrix" */ './pages/issues/matrix.vue')

const ControlUpdate = () =>
  import(/* webpackChunkName: "control" */ './pages/control/update.vue')
const ControlUpdateMatrix = () =>
  import(/* webpackChunkName: "control" */ './pages/control/update_matrix.vue')
const ControlUpdateSummary = () =>
  import(/* webpackChunkName: "control" */ './pages/control/update_summary.vue')
const ControlUpdateSummaryByAanalyser = () =>
  import(
    /* webpackChunkName: "control" */ './pages/control/update_summary_by_analyser.vue'
  )

Vue.use(VueRouter)

export const router = new VueRouter({
  mode: 'history',
  routes: [
    { path: '/:lang/', component: Index },
    { path: '/:lang/contact', component: Contact },
    { path: '/:lang/copyright', component: Copyright },
    { path: '/:lang/translation', component: Translation },

    { path: '/:lang/map/', component: Map },

    { path: '/:lang/issue/:uuid', component: IssueIndex },
    { path: '/:lang/issues/open', component: IssuesIndex, name: 'issues/open' },
    { path: '/:lang/issues/done', component: IssuesIndex, name: 'issues/done' },
    {
      path: '/:lang/issues/false-positive',
      component: IssuesIndex,
      name: 'issues/false-positive',
    },
    { path: '/:lang/false-positive/:uuid', component: IssueIndex },
    { path: '/:lang/issues/matrix', component: IssuesMatrix },
    { path: '/:lang/byuser', component: ByUserIndex },
    { path: '/:lang/byuser/:user', component: ByUserList },

    { path: '/:lang/control/update/:source_id', component: ControlUpdate },
    { path: '/:lang/control/update_matrix', component: ControlUpdateMatrix },
    { path: '/:lang/control/update_summary', component: ControlUpdateSummary },
    {
      path: '/:lang/control/update_summary_by_analyser',
      component: ControlUpdateSummaryByAanalyser,
    },

    { path: '*', component: NotFound },
  ],
})
