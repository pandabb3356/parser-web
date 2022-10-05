import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex)

const state = {
  sidebarShow: 'responsive',
  sidebarMinimize: false,
}

const mutations = {
  toggleSidebarDesktop (state) {
    const sidebarOpened = [true, 'responsive'].includes(state.sidebarShow)
    state.sidebarShow = sidebarOpened ? false : 'responsive'
  },
  toggleSidebarMobile (state) {
    const sidebarClosed = [false, 'responsive'].includes(state.sidebarShow)
    state.sidebarShow = sidebarClosed ? true : 'responsive'
  },
  set (state, [variable, value]) {
    state[variable] = value
  }
}


const globalModule = {
  namespaced: true,
  getters: {
    getUser(state) {
      return state.user;
    }
  },
  state: () => {
    return {
      user: {
        authenticated: false,
        sessionId: ""
      },
      cleanUser() {
        window.localStorage.removeItem('user');
      },
      initUser() {
        return {
          authenticated: false,
          sessionId: ""
        }
      }
    }
  },
  mutations: {
    setUser(state, user) {
      state.user.authenticated = true;
      state.user.id = user.id;
      state.user.name = user.name;
      state.user.email = user.email;
    },
    cleanUser(state) {
      state.cleanUser();
      state.user = state.initUser();
    },
  },
};

export default new Vuex.Store({
  state,
  mutations,
  modules: {
    global: globalModule
  },
})