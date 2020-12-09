import i18n from './config/i18n.js'

let development = process.env.NODE_ENV !== 'production'

export default {
  // Disable server-side rendering (https://go.nuxtjs.dev/ssr-mode)
  ssr: false,

  // Global page headers (https://go.nuxtjs.dev/config-head)
  head: {
    title: 'Barney - document versioning system',
    meta: [
      { charset: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { hid: 'description', name: 'description', content: '' }
    ],
    link: [
      { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' }
    ]
  },

  // Global CSS (https://go.nuxtjs.dev/config-css)
  css: [
  ],

  // Plugins to run before rendering page (https://go.nuxtjs.dev/config-plugins)
  plugins: [
  ],

  // Auto import components (https://go.nuxtjs.dev/config-components)
  components: true,

  // Modules for dev and build (recommended) (https://go.nuxtjs.dev/config-modules)
  buildModules: [
    // https://go.nuxtjs.dev/eslint
    '@nuxtjs/eslint-module',
    //'@nuxtjs/proxy',
  ],

  // Modules (https://go.nuxtjs.dev/config-modules)
  modules: [
    // https://go.nuxtjs.dev/buefy
    'nuxt-buefy',
    // https://go.nuxtjs.dev/axios
    '@nuxtjs/axios',
    //'@nuxtjs/proxy',
    ['cookie-universal-nuxt', { alias: 'cookiz' }],
    [
      'nuxt-i18n',
      {
        defaultLocale: 'it',
        vueI18nLoader: true,
         locales: [
          {
             code: 'en',
             name: 'English'
          },
          {
             code: 'it',
             name: 'Italiano'
          }
        ],
        vueI18n: i18n
      }
     ]
  ],


  proxy: {
    '/': {
      target: 'http://localhost',
      pathRewrite: {
        '^/' : '/'
        }
      }
  },

  router: {
    routes: [
      {
        name: 'index',
        path: '/:id?',
        component: 'layouts/default.vue'
      },
    ]
  },
  

  // Axios module configuration (https://go.nuxtjs.dev/config-axios)
  axios: {
    //baseURL: 'http://localhost:8000',
    baseURL: 'http://10.10.21.50:8989',
    //baseURL: development ? 'http://localhost:8000' : 'http://172.25.193.167:8088'
    //proxyHeaders: false,
    //credentials: false
  },
  generate: {
    dir: '../version/static/version/frontend'
  },
  // Build Configuration (https://go.nuxtjs.dev/config-build)
  build: {
    dir: '../version/static/version/frontend',
    extend (config, { isDev, isClient }) {
      if (!isDev) {
        // relative links, please.
        config.output.publicPath = './_nuxt/'
      }
      return config;
    }
  },
  server: {
      host: "0.0.0.0"
  }
}
