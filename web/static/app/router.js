import Vue from 'vue'
import VueRouter from 'vue-router'

const Index = () =>
    import ( /* webpackChunkName: "index" */ './pages/index.vue');
const Contact = () =>
    import ( /* webpackChunkName: "contact" */ './pages/contact.vue');
const Copyright = () =>
    import ( /* webpackChunkName: "copyright" */ './pages/copyright.vue');
const Translation = () =>
    import ( /* webpackChunkName: "translation" */ './pages/translation.vue');

const IssueIndex = () =>
    import ( /* webpackChunkName: "issue" */ './pages/issue/index.vue');
const FalsepositiveIndex = () =>
    import ( /* webpackChunkName: "issue" */ './pages/false-positive/index.vue');
const IssuesIndex = () =>
    import ( /* webpackChunkName: "issues" */ './pages/issues/index.vue');
const ByUserIndex = () =>
    import ( /* webpackChunkName: "issues" */ './pages/byuser/index.vue');
const ByUserList = () =>
    import ( /* webpackChunkName: "issues" */ './pages/byuser/byuser.vue');
const IssuesMatrix = () =>
    import ( /* webpackChunkName: "issues_matrix" */ './pages/issues/matrix.vue');

const ControlUpdate = () =>
    import ( /* webpackChunkName: "control" */ './pages/control/update.vue');
const ControlUpdates = () =>
    import ( /* webpackChunkName: "control" */ './pages/control/updates.vue');
const ControlUpdateMatrix = () =>
    import ( /* webpackChunkName: "control" */ './pages/control/update_matrix.vue');
const ControlUpdateSummary = () =>
    import ( /* webpackChunkName: "control" */ './pages/control/update_summary.vue');
const ControlUpdateSummaryByAanalyser = () =>
    import ( /* webpackChunkName: "control" */ './pages/control/update_summary_by_analyser.vue');


Vue.use(VueRouter)

export const router = new VueRouter({
    mode: 'history',
    routes: [
        { path: '/:lang/', component: Index },
        { path: '/:lang/contact', component: Contact },
        { path: '/:lang/copyright', component: Copyright },
        { path: '/:lang/translation', component: Translation },

        { path: '/:lang/error/:uuid', component: IssueIndex },
        { path: '/:lang/errors/', component: IssuesIndex, name: 'issues/open' },
        { path: '/:lang/errors/done', component: IssuesIndex, name: 'issues/done' },
        { path: '/:lang/errors/false-positive', component: IssuesIndex, name: 'issues/false-positive' },
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
