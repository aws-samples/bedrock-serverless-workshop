import Vue from 'vue'
import App from './App.vue'
import axios from 'axios'
import router from './router'
import VueAxios from 'vue-axios'

Vue.config.productionTip = false

axios.defaults.baseURL = "Replace with API Gateway URL"
Vue.prototype.$UserPoolId = 'Replace COGNITO User Pool'
Vue.prototype.$ClientId = 'Replace User Pool App Client ID'

Vue.use(VueAxios, axios)

Vue.config.productionTip = false

new Vue({
router,
  render: h => h(App),

}).$mount('#app')
