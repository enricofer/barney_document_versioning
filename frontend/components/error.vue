<template>
  <div>
      <b-modal v-model="errorDialog" :width="420" scroll="keep">
      <div class="card">
        <header class="card-header">
          <p class="card-header-title">
            {{ $t('Error') }}
          </p>
        </header>

        <div class="card-content">
          <section>
              <b-notification
                  type="is-danger"
                  has-icon
                  aria-close-label="Error"
                  v-model="error"
                  role="alert">
                  {{ errorMessage }}
              </b-notification>
          </section>
        </div>

        <footer class="card-footer">
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
      errorMessage: "",
      errorDialog: false

    }
  }, 

  mounted () {
    //this.$nuxt.$on('refreshTree', this.fetchVersions)
    this.$nuxt.$on('error', this.openErrorDialog)
  },

  methods: {

    openErrorDialog(message) {
      this.errorMessage = message
      this.errorDialog = true
    },

    close () {
        this.errorMessage = ""
        this.errorDialog = false
        this.$nuxt.$emit('refreshTree')
    }
  },

}
</script>