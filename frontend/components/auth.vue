<template>
  <div>
      <b-button type="is-info" inverted outlined rounded @click="credentials()">{{ getLoggedUser() }}</b-button>
      <b-modal v-model="loginPanel" :width="420" scroll="keep">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">
            {{ $t('Login') }}
          </p>
        </header>

        <div class="card-content">
          <section>
              <b-field label="Login">
                  <b-input v-model="username"></b-input>
              </b-field>

              <b-field label="Password">
                  <b-input type="password" v-model="password" password-reveal>
                  </b-input>
              </b-field>

              <b-notification
                  type="is-danger"
                  has-icon
                  aria-close-label="Close notification"
                  v-model="loginError"
                  role="alert">
                  {{ $t('Invalid credentials') }}
              </b-notification>

              <b-notification
                  type="is-info"
                  has-icon
                  aria-close-label="Close notification"
                  v-model="loggedOut"
                  role="alert">
                  Logged out
              </b-notification>
          </section>
        </div>

        <footer class="card-footer">
          <a href="#" type="is-danger" class="card-footer-item" @click="login()">{{ $t('Login') }}</a>
          <a href="#" type="is-danger" class="card-footer-item" @click="logout()">{{ $t('Logout') }}</a>
          <a href="#" class="card-footer-item" @click="loginPanel = false">{{ $t('Close') }}</a>
        </footer>

      </div>
    </b-modal>
  </div>
</template>

<style>

</style>

<script>
/* eslint-disable */

export default {
  data () {
    return {
      username: undefined,
      password: undefined,
      expiresIn: 10000,
      token: "",
      loginPanel: false,
      loginError: false,
      loggedOut: false,
      errorMessage: "",
      refreshTimer: undefined

    }
  }, 

  components: {

  },

  mounted () {
    //this.$nuxt.$on('refreshTree', this.fetchVersions)
    this.$nuxt.$on('askCredentials', this.credentials)
    this.$nuxt.$on('Authenticated', this.setRefresh)
    const cookied_token = this.$cookiz.get('barney_token')
    console.log("Cookie",cookied_token)
    if (cookied_token) {
      this.username = cookied_token.username
      this.token = cookied_token.token
      this.expiresIn = !cookied_token.expiresIn ? 5000 : cookied_token.expiresIn
      this.$axios.setToken(this.token, 'Bearer')
      const T = this
      setTimeout(function(){
        T.$nuxt.$emit('Authenticated', T.username)
      },200)
    } else {
      this.credentials()
    }
  },

  methods: {

    getLoggedUser() {
      if (this.username) return this.username
      return 'Login'
    },

    logout() {
      this.username = undefined
      this.token = undefined
      this.$cookiz.remove('barney_token')
      this.loggedOut = true
      this.$axios.setToken(false)
      this.$nuxt.$emit('Authenticated', undefined)
    },

    credentials() {
      this.loggedOut = false
      this.loginError = false
      this.loginPanel = true
    },

    setRefresh (username) {
      if (!username) return
      const T = this
      this.refreshTimer = setInterval(function () {  
          const body = {
            token: T.token
          }
          T.$axios.$post('/version/token-refresh/', body).then(res=> {
            console.log("Token refreshed", res)
          })
      },  T.expiresIn*100 ) //(T.expiresIn - 10)*1000) (T.expiresIn/4)*1000
      console.log("Auth Token Refreshing in: ", this.expiresIn/10 )
    },
    
    login () {
      const payload = {
        username: this.username,
        password: this.password,
      }
      this.$axios.$post('/version/token-auth/', payload).then(res_login => {
          console.log("TIMER", res_login.expiresIn )
          this.password = undefined
          this.loginPanel = false
          this.loginError = false
          this.token = res_login.token
          res_login.username = this.username
          this.$cookiz.set('barney_token',JSON.stringify(res_login))
          this.expiresIn = !res_login.expiresIn ? res_login.expires_in : res_login.expiresIn //jwt outputs expires time with different keys
          this.$axios.setToken(this.token, 'Bearer')
          this.$nuxt.$emit('Authenticated', this.username)
      });
    },
    close () {
        this.loginPanel = false
        this.loginError = false
        this.username = undefined
        this.password = undefined
        clearTimeout(this.refreshTimer);
        this.$nuxt.$emit('Authenticated', undefined)
    }
  },

}
</script>