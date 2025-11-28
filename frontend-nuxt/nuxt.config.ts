// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: '2025-07-15',
  devtools: { enabled: true },
  css: ['~/assets/css/main.css'],
  modules: ['@pinia/nuxt'],
  
  app: {
    head: {
      link: [
        { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
        { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
        { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap' },
        { rel: 'stylesheet', href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css' }
      ]
    }
  },
  
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8080',
      firebase: {
        apiKey: "AIzaSyANDCAB8VI00JIVoRKLyXtc2FateShvn_c",
        authDomain: "linkedscrapper.firebaseapp.com",
        projectId: "linkedscrapper",
        storageBucket: "linkedscrapper.firebasestorage.app",
        messagingSenderId: "537959019488",
        appId: "1:537959019488:web:945b43c36a4bb6c198f185",
        measurementId: "G-HFP9095PCP"
      }
    }
  }
})
