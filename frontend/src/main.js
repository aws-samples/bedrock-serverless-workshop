import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import router from './router'
import VueAxios from 'vue-axios'

Vue.config.productionTip = false

//These values are replaces during amplify setup
axios.defaults.baseURL = "https://pco7cayzwg.execute-api.us-west-2.amazonaws.com/prod"
Vue.prototype.$UserPoolId = 'us-west-2_xH4JftIZe' 
Vue.prototype.$ClientId = '12lje4minlk73fme0uccji9sjm'

Vue.use(VueAxios, axios)

Vue.config.productionTip = false

new Vue({
router,
  render: h => h(App),

}).$mount('#app')
