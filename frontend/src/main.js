import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import router from './router'
import VueAxios from 'vue-axios'

Vue.config.productionTip = false

//These values are replaces during amplify setup
axios.defaults.baseURL = "https://7zx9ggptbh.execute-api.us-west-2.amazonaws.com/prod"
Vue.prototype.$UserPoolId = 'us-west-2_CzQMNqHpx'
Vue.prototype.$ClientId = '2sf30r4n00kuea1ju3a9kalo1p'

Vue.use(VueAxios, axios)

Vue.config.productionTip = false

new Vue({
router,
  render: h => h(App),

}).$mount('#app')
