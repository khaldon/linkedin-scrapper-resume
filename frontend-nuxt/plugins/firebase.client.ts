import { initializeApp } from 'firebase/app'
import { getAuth } from 'firebase/auth'

export default defineNuxtPlugin((nuxtApp) => {
  const config = {
    apiKey: "AIzaSyANDCAB8VI00JIVoRKLyXtc2FateShvn_c",
    authDomain: "linkedscrapper.firebaseapp.com",
    projectId: "linkedscrapper",
    storageBucket: "linkedscrapper.firebasestorage.app",
    messagingSenderId: "537959019488",
    appId: "1:537959019488:web:945b43c36a4bb6c198f185",
    measurementId: "G-HFP9095PCP"
  }

  const app = initializeApp(config)
  const auth = getAuth(app)

  return {
    provide: {
      auth
    }
  }
})
