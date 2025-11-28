export default defineNuxtRouteMiddleware(async (to, from) => {
  const authStore = useAuthStore()
  
  // Wait for auth to initialize
  if (authStore.loading) {
     await authStore.initAuth()
  }

  if (!authStore.isAuthenticated && to.path !== '/') {
    return navigateTo('/')
  }
})
