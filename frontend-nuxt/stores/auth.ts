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
    user: null as any, // Using any for now to avoid complex User type import issues, or import User from firebase/auth
    loading: true,
    error: null as string | null
  }),

  getters: {
    isAuthenticated: (state) => !!state.user,
  },

  actions: {
    async syncUserWithBackend(user: any) {
      if (!user) return
      
      const config = useRuntimeConfig()
      const apiBase = config.public.apiBase
      
      try {
        const token = await user.getIdToken()
        await $fetch(`${apiBase}/api/auth/sync`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          }
        })
      } catch (error) {
        console.error('Error syncing user with backend:', error)
      }
    },

    async initAuth() {
      const { $auth } = useNuxtApp()
      
      return new Promise((resolve) => {
        onAuthStateChanged($auth, async (user) => {
          this.user = user
          this.loading = false
          
          if (user) {
            await this.syncUserWithBackend(user)
          }
          
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
        // onAuthStateChanged will handle the sync
      } catch (error: any) {
        console.error('Google Sign-In Error:', error)
        if (error.code === 'auth/popup-blocked') {
           await signInWithRedirect($auth, provider)
        } else {
          this.error = error.message
          throw error
        }
      }
    },

    async logout() {
      const { $auth } = useNuxtApp()
      try {
        await signOut($auth)
        this.user = null
      } catch (error: any) {
        console.error('Logout Error:', error)
        this.error = error.message
      }
    }
  }
})
