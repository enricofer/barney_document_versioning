
<template>
  <div>
    <b-navbar class="header has-shadow is-dark">
        <template slot="brand">
            <b-navbar-item>
              <a class="navbar-item" :href="linkTitle" >
                <h1 class="title">{{ title }}</h1>
              </a>
            </b-navbar-item>
        </template>

        <template slot="end">
            <b-navbar-item tag="div">
                <auth></auth>
            </b-navbar-item>
        </template>
    </b-navbar>

    <section class="main-content columns">
        <div class="container column is-3">
        <section class="section">
        <b-field>
          <p class="control">
              <b-button size="is-small" rounded class="button is-info" @click="fetchVersions()">{{ $t('Refresh') }}</b-button>
          </p>
          <b-input
            icon="magnify"
            expanded
            size="is-small"
            rounded
            type="search"
            :placeholder="$t('Search available documents')"
            v-model="searchText"
            @input="fetchVersions()"
          >
          </b-input>
        </b-field>
        <div id="tree_container">
          <Tree :data="versionsMetadata" draggable crossTree ref="tree1" @change="tree1Change">
            <div slot-scope="{data, store}">
              <b v-if="data.children && data.children.length" @click="store.toggleOpen(data)">
                {{data.open ? '-' : '+'}}&nbsp;
              </b>
              <span style="display:inline-flex" :id="'item_'+data.id.toString()" :class="data.status" @click="openVersion(data.id)">
                <span v-bind:class="{ current: data.id == currentId }">{{data.title}}
                  <b-tag v-if="data.owner != username" style="flex:1;" rounded type="is-link is-light">{{ data.owner }}</b-tag>
                  <b-tag v-if="data.status == 'Merge_req'" rounded type="is-warning">{{ $t('Merging') }}</b-tag>
                  <b-tag v-if="data.status == 'History'" rounded type="is-success">{{ $t('Merged') }}</b-tag>
                  <b-tag v-if="data.owner == username && !data.private" rounded type="is-info">{{ $t('Public') }}</b-tag>
                </span>
              </span>
            </div>
          </Tree>
        </div>
        </section>
      </div>

      <div class="container column is-9">
        <editor />
      </div>
    </section>
  </div>
</template>

<style>

.tree-node-inner{
  padding: 5px;
  border: 1px solid #ccc;
  cursor: pointer;
}

.tree-node-inner .Version{
  color:#0f77ea;
}

.tree-node-inner .Merge_req{
  color:#4e00a7;
}

.tree-node-inner .Conflicted{
  color:red;
}

.tree-node-inner .Reconciled{
  color:green;
}

.current {
  /*background-color: lightskyblue*/
  font-weight: bold;
}

.tree-node-inner .History{
  color:darkorchid;
}

.aside {
  max-height: 800px;
  overflow-y: auto;
  word-wrap: anywhere;
}

.title {
  color:gainsboro;
}
</style>

<script>
/* eslint-disable */
// import VTree from 'vue-vtree';
import {DraggableTree} from 'vue-draggable-nested-tree';
import axios from 'axios'

import auth from '~/components/auth'
import error from '~/components/error'
import editor from '~/components/editor'

export default {
  data () {
    return {
      show: false,
      data: null,
      current: null,
      title: '...',
      linkTitle: '',
      username: undefined,
      currentId: undefined,
      searchText:"",
      versionsMetadata: []
    }
  }, 

  components: {
    Tree: DraggableTree,
    error,
    auth,
  },

  mounted () {

    if (!window.webpackHotUpdate) {
          console.log('App In Static Mode', window.location.href)
    } else {
          console.log('App In Dev Mode');
    }

   console.log("INIT",this.$route.query.init)

    let configjson
    if ("init" in this.$route.query) {
      
      configjson = JSON.parse(this.$route.query.init)
    }

    this.getConfig(configjson)

    this.$nuxt.$on('Authenticated', this.authenticated)
    this.$nuxt.$on('newItem', this.unselect)
    this.$nuxt.$on('refreshTree', this.fetchVersions)
    this.$nuxt.$on('openVersion', this.openVersion)
    this.fetchVersions()
    console.log(this.$route.query)
    if ("version" in configjson)  {
      this.openVersion( parseInt(configjson["version"]) )
    } else if ("version" in this.$route.query) {
      this.openVersion( parseInt(this.$route.query.version) )
    }

  },

  methods: {

    async getConfig(config) {
        let connection
        if (config) { //garbage in config detection needed
            this.title = config.title
            this.linkTitle = config.link
            this.$axios.defaults.baseURL = config.backend
            this.$i18n.setLocale(config.lang)
        } else {
          let base = window.location.host
          if (window.location.path != '/'){
            base = base.substr(0,base.lastIndexOf('/'))
          }
          connection = {url: 'barney_config.json', baseURL: base }
          console.log("connection", connection, configUrl)
          await this.$axios(connection).then(response =>{
              console.log("init json",response,this.title,this.$axios.defaults)
              this.title = response.data.title
              this.linkTitle = response.data.link
              this.$axios.defaults.baseURL = response.data.backend
              this.$i18n.setLocale(response.data.lang)
          })
        }
    },

    authenticated(username) {
      if (!username) {
        this.versionsMetadata = []
      } else {
        this.username = username;
        this.fetchVersions()
      }
    },

    tree1Change(node, targetTree) {
      this.data = targetTree.getPureData()
    },

    unselect() {
      this.currentId = undefined
    },

    openVersionByDetails(details) {
      const details_obj = JSON.parse(details)
      console.log("openVersionByDetails",details_obj)
      this.openVersion(details_obj.id)
    },

    async openVersion(id) {
      console.log("openVersion", id)
      await this.$axios.$get('/version/details/' + id.toString() + "/").then(response =>{
        this.currentId = id
        self.$nuxt.$emit('versionOpened', response)
      }).catch(response =>{
        console.log("ERROR",response)
        self.$nuxt.$emit('error',response["result"])
      })
    },

    async fetchVersions() {
      this.current = null
      console.log("fetchVersions")
      let q = ''
      if (this.searchText != "") {
        q = "?q="+this.searchText
      }
      await this.$axios.$get('/version/tree/0/'+q).then(response =>{
        console.log(response)
        this.versionsMetadata = response.versions
      }).catch(response =>{
        console.log("ERROR",response)
        this.versionsMetadata = []
        self.$nuxt.$emit('askCredentials')
      })
    }

  },

}
</script>


