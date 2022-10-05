import 'core-js/stable'
import Vue from 'vue'
import axios from 'axios'
import App from './App'
import router from './router'
import CoreuiVue from '@coreui/vue'
import { iconsSet as icons } from './assets/icons/icons.js'
import store from './store'
import VueAxios from 'vue-axios'
import jQuery from "jquery";

const $ = jQuery;
window.$ = $;


import config from './config'

Vue.config.performance = true
Vue.use(CoreuiVue)
Vue.prototype.$log = console.log.bind(console)
Vue.use(VueAxios, axios)

// toast
import VueToast from 'vue-toast-notification';
// Import one of the available themes
import 'vue-toast-notification/dist/theme-sugar.css';

Vue.use(VueToast);

window.Vue = Vue;

// filters
import { datetime } from "./filters/datetime"
import { toInt } from "./filters/toInt"
Vue.filter("datetime", datetime);
Vue.filter("toInt", toInt);

new Vue({
  el: '#app',
  router,
  store,
  icons,
  template: '<App/>',
  components: {
    App
  }
})
