import Vue from './vue.js'

import {
  Navbar
} from './components/navbar.js'

import {
  MainTemplate
} from './templates/main-template.js'


new Vue({
  el: '#app', // This should be the same as your <div id=""> from earlier.
  components: {
    'navbar': Navbar
  },
  template: MainTemplate
})