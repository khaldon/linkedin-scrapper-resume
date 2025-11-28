import { defineStore } from 'pinia'
import { 
  GoogleAuthProvider, 
  signInWithPopup, 
  signInWithRedirect, 
  signOut, 
  onAuthStateChanged 
} from 'firebase/auth'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    loading: true,
    error: null
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
  },

  actions: {
    async initAuth() {
      const { $auth } = useNuxtApp()
      
      return new Promise((resolve) => {
        onAuthStateChanged($auth, (user) => {
          this.user = user
          this.loading = false
          resolve(user)
        })
      })
    },

    async loginWithGoogle() {
      const { $auth } = useNuxtApp()
      const provider = new GoogleAuthProvider()
      provider.addScope('profile')
      provider.addScope('email')
      
      try {
        this.error = null
        await signInWithPopup($auth, provider)
      } catch (error) {
        console.error('Google Sign-In Error:', error)
        if (error.code === 'auth/popup-blocked') {
           await signInWithRedirect($auth, provider)
        } else {
          this.error = error.message
        }
      }
    },

    async logout() {
      const { $auth } = useNuxtApp()
      try {
        await signOut($auth)
        this.user = null
      } catch (error) {
        console.error('Logout Error:', error)
        this.error = error.message
      }
    }
  }
})
