import Vue from 'vue'
import Router from 'vue-router'
import OrgVersions from "@/views/parser/OrgVersions";
import OrgToggles from "@/views/parser/OrgToggles";
import VersionRecords from "@/views/parser/VersionRecords";
import ToggleRecords from "../views/parser/ToggleRecords";

// Containers
const TheContainer = () => import('@/containers/TheContainer')

// Views
const Dashboard = () => import('@/views/Dashboard')

// Org
const OrgList = () => import('@/views/orgs/OrgList')
const OrgDetail = () => import('@/views/orgs/OrgDetail')

// Login
const Login = () => import('@/views/login/Login')

// store
import store from '@/store'

Vue.use(Router);


const routerReplace = Router.prototype.replace
Router.prototype.replace = function replace(location) {
  return routerReplace.call(this, location).catch(error => error)
};

const router = new Router({
  mode: 'hash', // https://router.vuejs.org/api/#mode
  linkActiveClass: 'active',
  scrollBehavior: () => ({ y: 0 }),
  routes: configRoutes()
})

function configRoutes () {
  return [
    {
      path: '/',
      redirect: '/dashboard',
      name: 'Home',
      component: TheContainer,
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: Dashboard
        },
        {
          path: 'org',
          redirect: '/org/list',
          name: 'Org',
          component: {
            render (c) { return c('router-view') }
          },
          children: [
            {
              path: 'list',
              name: 'Org List',
              component: OrgList
            },
            {
              path: 'add',
              name: 'New Org',
              component: OrgDetail,
            },
            {
              path: ':id',
              name: 'Org Detail',
              component: OrgDetail,
            },

          ]
        },
        {
          path: 'version',
          meta: {
            label: 'Version Records'
          },
          component: {
            render (c) { return c('router-view') }
          },
          children: [
            {
              path: '',
              name: 'Version Records',
              component: VersionRecords,
            },
            {
              path: ':id',
              name: 'Versions',
              meta: {
                label: "Version Details"
              },
              component: OrgVersions,
              props: (route) => ({
                  ...route.params
              })
            },
          ]
        },
        {
          path: 'toggle',
          meta: {
            label: 'Toggle Records'
          },
          component: {
            render (c) { return c('router-view') }
          },
          children: [
            {
              path: '',
              name: 'Toggle Records',
              component: ToggleRecords,
            },
            {
              path: ':id',
              name: 'Toggles Details',
              meta: {
                label: "Toggles Details"
              },
              component: OrgToggles,
              props: (route) => ({
                  ...route.params
              })
            },
          ]
        },
      ]
    },
    {
      path: '/login',
      name: 'Login',
      component: Login,
      meta: {
        requiresAuth: false
      }
    },
  ]
}

router.beforeEach((to, from, next) => {
  const userStr = window.localStorage.getItem('user');
  if (userStr) {
    const now = new Date();
    const user = JSON.parse(userStr);
    if (user.expiredAt && now.getTime() < user.expiredAt) {
      store.commit("global/setUser", user, {root: true});
    } else {
      store.commit("global/cleanUser");
    }
  }

  if (to.matched.some(record => record.meta.requiresAuth === false)) {
    next();
  } else {
    if (store.getters["global/getUser"].authenticated) {
      next();
    } else {
      next({ name: "Login"});
    }
  }
});

export default router;
